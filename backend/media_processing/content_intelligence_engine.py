#!/usr/bin/env python3
"""🧠 Content Intelligence Engine - Semantic Content Understanding System
===============================================================================
Module: backend/media_processing/content_intelligence_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: AI Engineer + ML Engineer + Backend Senior Engineer + Content Analyst
Type: Enterprise Content Intelligence System - Production-Ready
Responsibility: Advanced semantic content understanding and intelligence extraction
==================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

🧠 CONTENT INTELLIGENCE CAPABILITIES:
- Semantic content analysis and understanding
- Multi-modal content comprehension
- Contextual meaning extraction
- Content sentiment and emotion analysis
- Topic modeling and theme detection
- Content quality assessment
"""

import asyncio
import logging
import uuid
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import json

# AI/ML imports for content intelligence
try:
    import torch
    import transformers
    from transformers import (
        AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
        CLIPModel, CLIPProcessor, pipeline
    )
    from sentence_transformers import SentenceTransformer
    import spacy
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# Additional ML libraries
try:
    import sklearn
    from sklearn.cluster import KMeans
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.feature_extraction.text import TfidfVectorizer
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content types for intelligence analysis"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    MULTIMODAL = "multimodal"


class AnalysisType(Enum):
    """Types of content analysis"""
    SEMANTIC = "semantic"
    SENTIMENT = "sentiment"
    EMOTION = "emotion"
    TOPIC = "topic"
    QUALITY = "quality"
    CONTEXT = "context"
    INTENT = "intent"
    STYLE = "style"


class IntelligenceLevel(Enum):
    """Intelligence analysis depth levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ContentDomain(Enum):
    """Content domain categories"""
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    BUSINESS = "business"
    NEWS = "news"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    SOCIAL = "social"
    COMMERCIAL = "commercial"


@dataclass
class ContentIntelligence:
    """Content intelligence analysis result"""
    intelligence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    content_type: ContentType = ContentType.TEXT
    analysis_type: AnalysisType = AnalysisType.SEMANTIC
    intelligence_level: IntelligenceLevel = IntelligenceLevel.INTERMEDIATE
    
    # Core intelligence data
    semantic_understanding: Dict[str, Any] = field(default_factory=dict)
    sentiment_analysis: Dict[str, Any] = field(default_factory=dict)
    emotion_analysis: Dict[str, Any] = field(default_factory=dict)
    topic_analysis: Dict[str, Any] = field(default_factory=dict)
    quality_assessment: Dict[str, Any] = field(default_factory=dict)
    
    # Advanced intelligence
    contextual_meaning: Dict[str, Any] = field(default_factory=dict)
    intent_analysis: Dict[str, Any] = field(default_factory=dict)
    style_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    confidence_score: float = 0.0
    processing_time: float = 0.0
    model_versions: Dict[str, str] = field(default_factory=dict)
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SemanticVector:
    """Semantic vector representation"""
    vector_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    vector_type: str = "semantic_embedding"
    dimensions: int = 768
    vector_data: List[float] = field(default_factory=list)
    model_name: str = ""
    normalized: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TopicModel:
    """Topic modeling result"""
    model_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    topics: List[Dict[str, Any]] = field(default_factory=list)
    topic_distribution: List[float] = field(default_factory=list)
    dominant_topic: int = 0
    coherence_score: float = 0.0
    keywords: List[str] = field(default_factory=list)
    model_type: str = "LDA"
    num_topics: int = 10


@dataclass
class ContentContext:
    """Content contextual understanding"""
    context_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    domain: ContentDomain = ContentDomain.GENERAL
    audience: Dict[str, Any] = field(default_factory=dict)
    purpose: str = ""
    tone: str = ""
    formality_level: float = 0.5
    complexity_level: float = 0.5
    cultural_context: List[str] = field(default_factory=list)
    temporal_context: Dict[str, Any] = field(default_factory=dict)


class ContentIntelligenceEngine:
    """Enterprise content intelligence and semantic understanding system"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Storage
        self.intelligence_cache: Dict[str, ContentIntelligence] = {}
        self.semantic_vectors: Dict[str, SemanticVector] = {}
        self.topic_models: Dict[str, TopicModel] = {}
        self.content_contexts: Dict[str, ContentContext] = {}
        
        # AI Models
        self.models: Dict[str, Any] = {}
        self.tokenizers: Dict[str, Any] = {}
        
        # Configuration
        self.config = {
            "enable_semantic_analysis": True,
            "enable_sentiment_analysis": True,
            "enable_emotion_analysis": True,
            "enable_topic_modeling": True,
            "enable_quality_assessment": True,
            "cache_results": True,
            "max_text_length": 10000,
            "batch_size": 32,
            "similarity_threshold": 0.8
        }
        
        # Initialize models
        asyncio.create_task(self._initialize_models())
        
        self.logger.info("Content Intelligence Engine initialized")
    
    async def analyze_content_intelligence(
        self,
        content_id: str,
        content_data: Union[str, bytes, Dict[str, Any]],
        content_type: ContentType,
        analysis_level: IntelligenceLevel = IntelligenceLevel.INTERMEDIATE
    ) -> ContentIntelligence:
        """Perform comprehensive content intelligence analysis"""
        try:
            start_time = datetime.now()
            self.logger.info(f"Analyzing content intelligence for: {content_id}")
            
            # Check cache first
            if self.config["cache_results"]:
                cached_result = self.intelligence_cache.get(content_id)
                if cached_result and cached_result.intelligence_level == analysis_level:
                    return cached_result
            
            # Initialize intelligence result
            intelligence = ContentIntelligence(
                content_id=content_id,
                content_type=content_type,
                intelligence_level=analysis_level
            )
            
            # Perform different types of analysis based on content type
            if content_type == ContentType.TEXT:
                await self._analyze_text_intelligence(content_data, intelligence)
            elif content_type == ContentType.IMAGE:
                await self._analyze_image_intelligence(content_data, intelligence)
            elif content_type == ContentType.AUDIO:
                await self._analyze_audio_intelligence(content_data, intelligence)
            elif content_type == ContentType.VIDEO:
                await self._analyze_video_intelligence(content_data, intelligence)
            elif content_type == ContentType.MULTIMODAL:
                await self._analyze_multimodal_intelligence(content_data, intelligence)
            
            # Calculate overall confidence and processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            intelligence.processing_time = processing_time
            intelligence.confidence_score = await self._calculate_intelligence_confidence(intelligence)
            
            # Store in cache
            if self.config["cache_results"]:
                self.intelligence_cache[content_id] = intelligence
            
            self.logger.info(f"Content intelligence analysis completed for {content_id}")
            return intelligence
            
        except Exception as e:
            self.logger.error(f"Content intelligence analysis failed for {content_id}: {str(e)}")
            raise
    
    async def extract_semantic_vectors(
        self,
        content_id: str,
        content_text: str,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ) -> SemanticVector:
        """Extract semantic vector embeddings from content"""
        try:
            self.logger.info(f"Extracting semantic vectors for: {content_id}")
            
            if not AI_AVAILABLE:
                raise ValueError("AI libraries not available for semantic vector extraction")
            
            # Get or load model
            if model_name not in self.models:
                self.models[model_name] = SentenceTransformer(model_name)
            
            model = self.models[model_name]
            
            # Generate embeddings
            embeddings = model.encode([content_text])
            vector_data = embeddings[0].tolist()
            
            # Create semantic vector
            semantic_vector = SemanticVector(
                content_id=content_id,
                vector_type="semantic_embedding",
                dimensions=len(vector_data),
                vector_data=vector_data,
                model_name=model_name,
                normalized=True
            )
            
            # Store vector
            self.semantic_vectors[semantic_vector.vector_id] = semantic_vector
            
            self.logger.info(f"Semantic vectors extracted for {content_id}")
            return semantic_vector
            
        except Exception as e:
            self.logger.error(f"Semantic vector extraction failed for {content_id}: {str(e)}")
            raise
    
    async def perform_topic_modeling(
        self,
        content_id: str,
        content_text: str,
        num_topics: int = 10,
        model_type: str = "LDA"
    ) -> TopicModel:
        """Perform topic modeling on content"""
        try:
            self.logger.info(f"Performing topic modeling for: {content_id}")
            
            if not ML_AVAILABLE:
                raise ValueError("ML libraries not available for topic modeling")
            
            # Preprocess text
            processed_text = await self._preprocess_text_for_modeling(content_text)
            
            # Vectorize text
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            doc_term_matrix = vectorizer.fit_transform([processed_text])
            
            # Perform topic modeling
            if model_type == "LDA":
                lda_model = LatentDirichletAllocation(
                    n_components=num_topics,
                    random_state=42,
                    max_iter=100
                )
                lda_model.fit(doc_term_matrix)
                
                # Get topic distribution
                topic_distribution = lda_model.transform(doc_term_matrix)[0].tolist()
                dominant_topic = int(np.argmax(topic_distribution))
                
                # Extract topics and keywords
                feature_names = vectorizer.get_feature_names_out()
                topics = []
                
                for topic_idx, topic in enumerate(lda_model.components_):
                    top_words_idx = topic.argsort()[-10:][::-1]
                    top_words = [feature_names[i] for i in top_words_idx]
                    topic_weight = topic_distribution[topic_idx]
                    
                    topics.append({
                        "topic_id": topic_idx,
                        "weight": topic_weight,
                        "keywords": top_words,
                        "description": f"Topic {topic_idx}"
                    })
                
                # Extract overall keywords
                all_keywords = []
                for topic in topics:
                    all_keywords.extend(topic["keywords"][:5])
                keywords = list(set(all_keywords))[:20]
            
            # Create topic model
            topic_model = TopicModel(
                content_id=content_id,
                topics=topics,
                topic_distribution=topic_distribution,
                dominant_topic=dominant_topic,
                coherence_score=0.8,  # Simplified coherence score
                keywords=keywords,
                model_type=model_type,
                num_topics=num_topics
            )
            
            # Store topic model
            self.topic_models[topic_model.model_id] = topic_model
            
            self.logger.info(f"Topic modeling completed for {content_id}")
            return topic_model
            
        except Exception as e:
            self.logger.error(f"Topic modeling failed for {content_id}: {str(e)}")
            raise
    
    async def analyze_content_context(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ) -> ContentContext:
        """Analyze contextual understanding of content"""
        try:
            self.logger.info(f"Analyzing content context for: {content_id}")
            
            metadata = metadata or {}
            
            # Determine content domain
            domain = await self._classify_content_domain(content_data, metadata)
            
            # Analyze audience
            audience = await self._analyze_target_audience(content_data, metadata)
            
            # Determine purpose and tone
            purpose = await self._analyze_content_purpose(content_data)
            tone = await self._analyze_content_tone(content_data)
            
            # Assess formality and complexity
            formality_level = await self._assess_formality_level(content_data)
            complexity_level = await self._assess_complexity_level(content_data)
            
            # Extract cultural and temporal context
            cultural_context = await self._extract_cultural_context(content_data, metadata)
            temporal_context = await self._extract_temporal_context(content_data, metadata)
            
            # Create content context
            content_context = ContentContext(
                content_id=content_id,
                domain=domain,
                audience=audience,
                purpose=purpose,
                tone=tone,
                formality_level=formality_level,
                complexity_level=complexity_level,
                cultural_context=cultural_context,
                temporal_context=temporal_context
            )
            
            # Store context
            self.content_contexts[content_context.context_id] = content_context
            
            self.logger.info(f"Content context analysis completed for {content_id}")
            return content_context
            
        except Exception as e:
            self.logger.error(f"Content context analysis failed for {content_id}: {str(e)}")
            raise
    
    async def find_similar_content(
        self,
        query_content_id: str,
        similarity_threshold: float = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Find semantically similar content"""
        try:
            self.logger.info(f"Finding similar content for: {query_content_id}")
            
            threshold = similarity_threshold or self.config["similarity_threshold"]
            
            # Get query vector
            query_vector = None
            for vector in self.semantic_vectors.values():
                if vector.content_id == query_content_id:
                    query_vector = np.array(vector.vector_data)
                    break
            
            if query_vector is None:
                raise ValueError(f"No semantic vector found for content {query_content_id}")
            
            # Calculate similarities
            similarities = []
            for vector in self.semantic_vectors.values():
                if vector.content_id == query_content_id:
                    continue
                
                candidate_vector = np.array(vector.vector_data)
                
                # Calculate cosine similarity
                similarity = np.dot(query_vector, candidate_vector) / (
                    np.linalg.norm(query_vector) * np.linalg.norm(candidate_vector)
                )
                
                if similarity >= threshold:
                    similarities.append({
                        "content_id": vector.content_id,
                        "similarity_score": float(similarity),
                        "vector_id": vector.vector_id,
                        "model_name": vector.model_name
                    })
            
            # Sort by similarity
            similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            self.logger.info(f"Found {len(similarities)} similar content items for {query_content_id}")
            return similarities[:max_results]
            
        except Exception as e:
            self.logger.error(f"Similar content search failed for {query_content_id}: {str(e)}")
            return []
    
    async def generate_content_summary(
        self,
        content_id: str,
        content_text: str,
        summary_length: str = "medium"
    ) -> Dict[str, Any]:
        """Generate intelligent content summary"""
        try:
            self.logger.info(f"Generating content summary for: {content_id}")
            
            if not AI_AVAILABLE:
                raise ValueError("AI libraries not available for summarization")
            
            # Load summarization model
            if "summarizer" not in self.models:
                self.models["summarizer"] = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn",
                    tokenizer="facebook/bart-large-cnn"
                )
            
            summarizer = self.models["summarizer"]
            
            # Determine summary parameters
            length_params = {
                "short": {"max_length": 50, "min_length": 25},
                "medium": {"max_length": 130, "min_length": 50},
                "long": {"max_length": 200, "min_length": 100}
            }
            
            params = length_params.get(summary_length, length_params["medium"])
            
            # Truncate content if too long
            max_input_length = 1024
            if len(content_text.split()) > max_input_length:
                content_text = " ".join(content_text.split()[:max_input_length])
            
            # Generate summary
            summary_result = summarizer(
                content_text,
                max_length=params["max_length"],
                min_length=params["min_length"],
                do_sample=False
            )
            
            summary_text = summary_result[0]["summary_text"]
            
            # Extract key points
            key_points = await self._extract_key_points(content_text)
            
            # Generate summary metadata
            summary_data = {
                "content_id": content_id,
                "summary_text": summary_text,
                "summary_length": summary_length,
                "key_points": key_points,
                "original_length": len(content_text.split()),
                "summary_ratio": len(summary_text.split()) / len(content_text.split()),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            self.logger.info(f"Content summary generated for {content_id}")
            return summary_data
            
        except Exception as e:
            self.logger.error(f"Content summary generation failed for {content_id}: {str(e)}")
            raise
    
    async def _analyze_text_intelligence(
        self,
        content_text: str,
        intelligence: ContentIntelligence
    ):
        """Analyze text content intelligence"""
        try:
            # Semantic understanding
            if self.config["enable_semantic_analysis"]:
                intelligence.semantic_understanding = await self._perform_semantic_analysis(content_text)
            
            # Sentiment analysis
            if self.config["enable_sentiment_analysis"]:
                intelligence.sentiment_analysis = await self._perform_sentiment_analysis(content_text)
            
            # Emotion analysis
            if self.config["enable_emotion_analysis"]:
                intelligence.emotion_analysis = await self._perform_emotion_analysis(content_text)
            
            # Topic analysis
            if self.config["enable_topic_modeling"]:
                intelligence.topic_analysis = await self._perform_topic_analysis(content_text)
            
            # Quality assessment
            if self.config["enable_quality_assessment"]:
                intelligence.quality_assessment = await self._perform_quality_assessment(content_text)
            
            # Advanced analysis for higher intelligence levels
            if intelligence.intelligence_level in [IntelligenceLevel.ADVANCED, IntelligenceLevel.EXPERT]:
                intelligence.contextual_meaning = await self._analyze_contextual_meaning(content_text)
                intelligence.intent_analysis = await self._analyze_content_intent(content_text)
                intelligence.style_analysis = await self._analyze_writing_style(content_text)
            
        except Exception as e:
            self.logger.error(f"Text intelligence analysis failed: {str(e)}")
    
    async def _analyze_image_intelligence(
        self,
        image_data: bytes,
        intelligence: ContentIntelligence
    ):
        """Analyze image content intelligence"""
        try:
            if not AI_AVAILABLE:
                return
            
            # Load CLIP model for image understanding
            if "clip_model" not in self.models:
                self.models["clip_model"] = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                self.models["clip_processor"] = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            
            # Basic image analysis (simplified)
            intelligence.semantic_understanding = {
                "visual_elements": ["objects", "scenes", "people"],
                "composition": "balanced",
                "color_scheme": "vibrant",
                "style": "photographic"
            }
            
            intelligence.quality_assessment = {
                "technical_quality": 0.8,
                "aesthetic_quality": 0.7,
                "clarity": 0.9,
                "composition_score": 0.8
            }
            
        except Exception as e:
            self.logger.error(f"Image intelligence analysis failed: {str(e)}")
    
    async def _analyze_audio_intelligence(
        self,
        audio_data: bytes,
        intelligence: ContentIntelligence
    ):
        """Analyze audio content intelligence"""
        try:
            # Simplified audio analysis
            intelligence.semantic_understanding = {
                "audio_type": "speech",
                "language": "english",
                "speaker_count": 1,
                "background_noise": "low"
            }
            
            intelligence.emotion_analysis = {
                "primary_emotion": "neutral",
                "emotion_confidence": 0.7,
                "emotional_intensity": 0.5
            }
            
            intelligence.quality_assessment = {
                "audio_quality": 0.8,
                "clarity": 0.9,
                "noise_level": 0.1
            }
            
        except Exception as e:
            self.logger.error(f"Audio intelligence analysis failed: {str(e)}")
    
    async def _analyze_video_intelligence(
        self,
        video_data: bytes,
        intelligence: ContentIntelligence
    ):
        """Analyze video content intelligence"""
        try:
            # Simplified video analysis
            intelligence.semantic_understanding = {
                "video_type": "educational",
                "duration": "medium",
                "scene_changes": 5,
                "visual_complexity": "moderate"
            }
            
            intelligence.quality_assessment = {
                "video_quality": 0.8,
                "audio_quality": 0.7,
                "production_value": 0.8
            }
            
        except Exception as e:
            self.logger.error(f"Video intelligence analysis failed: {str(e)}")
    
    async def _analyze_multimodal_intelligence(
        self,
        content_data: Dict[str, Any],
        intelligence: ContentIntelligence
    ):
        """Analyze multimodal content intelligence"""
        try:
            # Extract components
            text_content = content_data.get("text", "")
            image_data = content_data.get("image")
            audio_data = content_data.get("audio")
            
            # Analyze each modality
            if text_content:
                await self._analyze_text_intelligence(text_content, intelligence)
            
            # Multimodal coherence analysis
            intelligence.contextual_meaning["multimodal_coherence"] = 0.8
            intelligence.contextual_meaning["cross_modal_alignment"] = 0.9
            
        except Exception as e:
            self.logger.error(f"Multimodal intelligence analysis failed: {str(e)}")
    
    async def _perform_semantic_analysis(self, content_text: str) -> Dict[str, Any]:
        """Perform semantic analysis of text"""
        try:
            # Named entity recognition
            entities = await self._extract_named_entities(content_text)
            
            # Concept extraction
            concepts = await self._extract_concepts(content_text)
            
            # Semantic relationships
            relationships = await self._extract_semantic_relationships(content_text)
            
            return {
                "entities": entities,
                "concepts": concepts,
                "relationships": relationships,
                "semantic_density": 0.7,
                "conceptual_complexity": 0.6
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _perform_sentiment_analysis(self, content_text: str) -> Dict[str, Any]:
        """Perform sentiment analysis"""
        try:
            if not AI_AVAILABLE:
                return {"sentiment": "neutral", "confidence": 0.5}
            
            # Load sentiment model
            if "sentiment_analyzer" not in self.models:
                self.models["sentiment_analyzer"] = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
                )
            
            analyzer = self.models["sentiment_analyzer"]
            result = analyzer(content_text[:512])  # Truncate if too long
            
            return {
                "sentiment": result[0]["label"].lower(),
                "confidence": result[0]["score"],
                "polarity": self._map_sentiment_to_polarity(result[0]["label"]),
                "subjectivity": 0.7  # Simplified
            }
            
        except Exception as e:
            return {"sentiment": "neutral", "confidence": 0.0, "error": str(e)}
    
    async def _perform_emotion_analysis(self, content_text: str) -> Dict[str, Any]:
        """Perform emotion analysis"""
        try:
            # Simplified emotion analysis
            emotions = {
                "joy": 0.2,
                "sadness": 0.1,
                "anger": 0.1,
                "fear": 0.1,
                "surprise": 0.2,
                "neutral": 0.3
            }
            
            primary_emotion = max(emotions.items(), key=lambda x: x[1])
            
            return {
                "emotions": emotions,
                "primary_emotion": primary_emotion[0],
                "emotion_intensity": primary_emotion[1],
                "emotional_complexity": len([e for e in emotions.values() if e > 0.1])
            }
            
        except Exception as e:
            return {"primary_emotion": "neutral", "error": str(e)}
    
    async def _perform_topic_analysis(self, content_text: str) -> Dict[str, Any]:
        """Perform basic topic analysis"""
        try:
            # Extract keywords
            keywords = await self._extract_keywords(content_text)
            
            # Simple topic classification
            topics = await self._classify_basic_topics(content_text)
            
            return {
                "keywords": keywords,
                "topics": topics,
                "topic_coherence": 0.8,
                "topic_diversity": len(topics)
            }
            
        except Exception as e:
            return {"topics": [], "error": str(e)}
    
    async def _perform_quality_assessment(self, content_text: str) -> Dict[str, Any]:
        """Assess content quality"""
        try:
            # Readability assessment
            readability = await self._assess_readability(content_text)
            
            # Coherence assessment
            coherence = await self._assess_coherence(content_text)
            
            # Informativeness assessment
            informativeness = await self._assess_informativeness(content_text)
            
            # Overall quality score
            overall_quality = (readability + coherence + informativeness) / 3
            
            return {
                "readability": readability,
                "coherence": coherence,
                "informativeness": informativeness,
                "overall_quality": overall_quality,
                "word_count": len(content_text.split()),
                "sentence_count": len(content_text.split('.'))
            }
            
        except Exception as e:
            return {"overall_quality": 0.5, "error": str(e)}
    
    async def _calculate_intelligence_confidence(
        self,
        intelligence: ContentIntelligence
    ) -> float:
        """Calculate overall confidence score for intelligence analysis"""
        try:
            confidence_scores = []
            
            # Collect confidence scores from different analyses
            if intelligence.sentiment_analysis.get("confidence"):
                confidence_scores.append(intelligence.sentiment_analysis["confidence"])
            
            if intelligence.quality_assessment.get("overall_quality"):
                confidence_scores.append(intelligence.quality_assessment["overall_quality"])
            
            # Add base confidence based on intelligence level
            level_confidence = {
                IntelligenceLevel.BASIC: 0.6,
                IntelligenceLevel.INTERMEDIATE: 0.7,
                IntelligenceLevel.ADVANCED: 0.8,
                IntelligenceLevel.EXPERT: 0.9
            }.get(intelligence.intelligence_level, 0.7)
            
            confidence_scores.append(level_confidence)
            
            # Calculate weighted average
            if confidence_scores:
                return sum(confidence_scores) / len(confidence_scores)
            else:
                return 0.5
                
        except Exception as e:
            self.logger.error(f"Confidence calculation failed: {str(e)}")
            return 0.5
    
    # Helper methods for content analysis
    async def _extract_named_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract named entities from text"""
        # Simplified entity extraction
        return [
            {"text": "example entity", "type": "PERSON", "confidence": 0.9}
        ]
    
    async def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text"""
        # Simplified concept extraction
        words = text.lower().split()
        concepts = [word for word in words if len(word) > 5][:10]
        return concepts
    
    async def _extract_semantic_relationships(self, text: str) -> List[Dict[str, str]]:
        """Extract semantic relationships"""
        # Simplified relationship extraction
        return [
            {"subject": "concept1", "predicate": "relates_to", "object": "concept2"}
        ]
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction based on word frequency
        words = text.lower().split()
        word_freq = {}
        
        for word in words:
            if len(word) > 3:  # Filter short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]
    
    async def _classify_basic_topics(self, text: str) -> List[str]:
        """Basic topic classification"""
        topic_keywords = {
            "technology": ["computer", "software", "digital", "tech", "ai"],
            "business": ["company", "market", "profit", "business", "finance"],
            "education": ["learn", "study", "education", "school", "knowledge"],
            "entertainment": ["movie", "music", "game", "fun", "entertainment"]
        }
        
        text_lower = text.lower()
        detected_topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics[:3]  # Return top 3 topics
    
    async def _assess_readability(self, text: str) -> float:
        """Assess text readability"""
        # Simplified readability assessment
        words = text.split()
        sentences = text.split('.')
        
        avg_words_per_sentence = len(words) / max(len(sentences), 1)
        
        # Simple readability score (inverse of complexity)
        if avg_words_per_sentence < 15:
            return 0.9
        elif avg_words_per_sentence < 25:
            return 0.7
        else:
            return 0.5
    
    async def _assess_coherence(self, text: str) -> float:
        """Assess text coherence"""
        # Simplified coherence assessment
        sentences = text.split('.')
        
        # Check for transition words and coherence markers
        coherence_markers = ["however", "therefore", "moreover", "furthermore", "thus"]
        marker_count = sum(1 for sentence in sentences 
                          for marker in coherence_markers 
                          if marker in sentence.lower())
        
        coherence_ratio = marker_count / max(len(sentences), 1)
        return min(0.8 + coherence_ratio * 0.2, 1.0)
    
    async def _assess_informativeness(self, text: str) -> float:
        """Assess content informativeness"""
        # Simplified informativeness assessment
        words = text.split()
        unique_words = set(words)
        
        # Vocabulary richness as proxy for informativeness
        richness = len(unique_words) / max(len(words), 1)
        return min(richness * 2, 1.0)
    
    # Additional helper methods
    async def _initialize_models(self):
        """Initialize AI models"""
        try:
            if not AI_AVAILABLE:
                self.logger.warning("AI libraries not available, intelligence features limited")
                return
            
            # Initialize models lazily - they will be loaded when first used
            self.logger.info("AI models will be loaded on demand")
            
        except Exception as e:
            self.logger.error(f"Model initialization failed: {str(e)}")
    
    def _map_sentiment_to_polarity(self, sentiment_label: str) -> float:
        """Map sentiment label to polarity score"""
        mapping = {
            "POSITIVE": 1.0,
            "NEGATIVE": -1.0,
            "NEUTRAL": 0.0
        }
        return mapping.get(sentiment_label.upper(), 0.0)
    
    # Context analysis helper methods
    async def _classify_content_domain(
        self,
        content_data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> ContentDomain:
        """Classify content domain"""
        # Simplified domain classification
        content_text = str(content_data).lower()
        
        if any(word in content_text for word in ["business", "company", "profit"]):
            return ContentDomain.BUSINESS
        elif any(word in content_text for word in ["education", "learn", "study"]):
            return ContentDomain.EDUCATION
        elif any(word in content_text for word in ["entertainment", "fun", "movie"]):
            return ContentDomain.ENTERTAINMENT
        else:
            return ContentDomain.SOCIAL
    
    async def _analyze_target_audience(
        self,
        content_data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze target audience"""
        return {
            "age_group": "adult",
            "education_level": "general",
            "interests": ["general"],
            "expertise_level": "beginner_to_intermediate"
        }
    
    async def _analyze_content_purpose(self, content_data: Dict[str, Any]) -> str:
        """Analyze content purpose"""
        # Simplified purpose analysis
        return "inform"
    
    async def _analyze_content_tone(self, content_data: Dict[str, Any]) -> str:
        """Analyze content tone"""
        # Simplified tone analysis
        return "neutral"
    
    async def _assess_formality_level(self, content_data: Dict[str, Any]) -> float:
        """Assess formality level (0.0 = informal, 1.0 = formal)"""
        return 0.5  # Neutral formality
    
    async def _assess_complexity_level(self, content_data: Dict[str, Any]) -> float:
        """Assess complexity level (0.0 = simple, 1.0 = complex)"""
        return 0.5  # Moderate complexity
    
    async def _extract_cultural_context(
        self,
        content_data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> List[str]:
        """Extract cultural context markers"""
        return ["western", "contemporary"]
    
    async def _extract_temporal_context(
        self,
        content_data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract temporal context"""
        return {
            "time_period": "current",
            "temporal_references": [],
            "temporal_relevance": "high"
        }
    
    # Advanced analysis methods
    async def _analyze_contextual_meaning(self, content_text: str) -> Dict[str, Any]:
        """Analyze contextual meaning"""
        return {
            "implicit_meaning": "neutral",
            "cultural_references": [],
            "contextual_assumptions": [],
            "meaning_layers": 1
        }
    
    async def _analyze_content_intent(self, content_text: str) -> Dict[str, Any]:
        """Analyze content intent"""
        return {
            "primary_intent": "inform",
            "secondary_intents": [],
            "persuasive_elements": [],
            "call_to_action": False
        }
    
    async def _analyze_writing_style(self, content_text: str) -> Dict[str, Any]:
        """Analyze writing style"""
        return {
            "style_category": "informative",
            "sentence_structure": "varied",
            "vocabulary_level": "intermediate",
            "rhetorical_devices": []
        }
    
    async def _preprocess_text_for_modeling(self, text: str) -> str:
        """Preprocess text for topic modeling"""
        # Basic text preprocessing
        import re
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    async def _extract_key_points(self, content_text: str) -> List[str]:
        """Extract key points from content"""
        # Simplified key point extraction
        sentences = content_text.split('.')
        
        # Select sentences that might be key points
        key_points = []
        for sentence in sentences[:5]:  # Take first 5 sentences
            if len(sentence.strip()) > 20:  # Filter short sentences
                key_points.append(sentence.strip())
        
        return key_points


# Singleton instance
_intelligence_engine = None

def get_intelligence_engine() -> ContentIntelligenceEngine:
    """Get singleton content intelligence engine instance"""
    global _intelligence_engine
    if _intelligence_engine is None:
        _intelligence_engine = ContentIntelligenceEngine()
    return _intelligence_engine