"""{{agent_name}} Content Analysis Agent for Ainflue Platform
import asyncio

{{agent_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum
import re
import hashlib

import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModel
from langdetect import detect
import spacy
from textstat import flesch_reading_ease, flesch_kincaid_grade
from pydantic import BaseModel, Field, validator

from ai.base_agent import BaseAIAgent
from ai.models import ContentAnalysisModelManager
from nlp.preprocessing import TextPreprocessor
from nlp.sentiment import SentimentAnalyzer
from nlp.topics import TopicModeling
from nlp.entities import EntityExtractor
from cv.analysis import VisualContentAnalyzer
from backend.audio.analysis import AudioContentAnalyzer
from core.config import get_settings
from utils.exceptions import ContentAnalysisException
from monitoring.content_metrics import ContentMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class ContentType(Enum):
    """Content types for analysis"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    MIXED_MEDIA = "mixed_media"


class AnalysisType(Enum):
    """Analysis types"""
    SENTIMENT = "sentiment"
    TOPIC_MODELING = "topic_modeling"
    ENTITY_EXTRACTION = "entity_extraction"
    LANGUAGE_DETECTION = "language_detection"
    READABILITY = "readability"
    CONTENT_QUALITY = "content_quality"
    PLAGIARISM = "plagiarism"
    TOXICITY = "toxicity"
    ENGAGEMENT_PREDICTION = "engagement_prediction"
    TREND_ANALYSIS = "trend_analysis"
    BRAND_SAFETY = "brand_safety"
    COPYRIGHT_CHECK = "copyright_check"


class ContentQualityMetrics(BaseModel):
    """Content quality metrics"""
    readability_score: float = Field(..., description="Readability score (0-100)")
    grammar_score: float = Field(..., description="Grammar correctness score (0-1)")
    uniqueness_score: float = Field(..., description="Content uniqueness score (0-1)")
    engagement_potential: float = Field(..., description="Predicted engagement potential (0-1)")
    seo_score: float = Field(..., description="SEO optimization score (0-1)")
    brand_safety_score: float = Field(..., description="Brand safety score (0-1)")


class ContentAnalysisTask(BaseModel):
    """Content analysis task"""
    id: str = Field(..., description="Unique task identifier")
    content_data: Union[str, bytes, Dict[str, Any]] = Field(..., description="Content to analyze")
    content_type: ContentType = Field(..., description="Type of content")
    analysis_types: List[AnalysisType] = Field(..., description="Types of analysis to perform")
    language: Optional[str] = Field(default=None, description="Content language (auto-detect if None)")
    target_audience: Optional[str] = Field(default=None, description="Target audience demographic")
    platform_context: Optional[str] = Field(default=None, description="Platform context (e.g., 'instagram', 'youtube')")
    include_suggestions: bool = Field(default=True, description="Include improvement suggestions")
    deep_analysis: bool = Field(default=False, description="Perform deep analysis (slower but more detailed)")
    priority: int = Field(default=1, description="Task priority (1-10)")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ContentEntity(BaseModel):
    """Extracted entity from content"""
    text: str = Field(..., description="Entity text")
    label: str = Field(..., description="Entity label/type")
    confidence: float = Field(..., description="Extraction confidence")
    start_pos: Optional[int] = Field(default=None, description="Start position in text")
    end_pos: Optional[int] = Field(default=None, description="End position in text")
    context: Optional[str] = Field(default=None, description="Surrounding context")


class ContentTopic(BaseModel):
    """Content topic"""
    topic_id: str = Field(..., description="Topic identifier")
    topic_name: str = Field(..., description="Human-readable topic name")
    keywords: List[str] = Field(..., description="Topic keywords")
    probability: float = Field(..., description="Topic probability")
    relevance_score: float = Field(..., description="Relevance score")


class ContentSuggestion(BaseModel):
    """Content improvement suggestion"""
    category: str = Field(..., description="Suggestion category")
    suggestion: str = Field(..., description="Improvement suggestion")
    impact: str = Field(..., description="Expected impact (low/medium/high)")
    implementation_effort: str = Field(..., description="Implementation effort (low/medium/high)")


class ContentAnalysisResult(BaseModel):
    """Content analysis result"""
    task_id: str = Field(..., description="Task identifier")
    success: bool = Field(..., description="Whether analysis succeeded")
    content_type: ContentType = Field(..., description="Type of content analyzed")
    language: Optional[str] = Field(default=None, description="Detected language")
    
    # Sentiment analysis results
    sentiment: Optional[Dict[str, float]] = Field(default=None, description="Sentiment scores")
    emotion_scores: Optional[Dict[str, float]] = Field(default=None, description="Emotion scores")
    
    # Topic and entity results
    topics: Optional[List[ContentTopic]] = Field(default=None, description="Detected topics")
    entities: Optional[List[ContentEntity]] = Field(default=None, description="Extracted entities")
    keywords: Optional[List[str]] = Field(default=None, description="Key terms/phrases")
    
    # Quality metrics
    quality_metrics: Optional[ContentQualityMetrics] = Field(default=None, description="Quality metrics")
    
    # Safety and compliance
    toxicity_score: Optional[float] = Field(default=None, description="Toxicity score (0-1)")
    brand_safety_issues: Optional[List[str]] = Field(default=None, description="Brand safety concerns")
    copyright_warnings: Optional[List[str]] = Field(default=None, description="Potential copyright issues")
    
    # Analysis insights
    content_summary: Optional[str] = Field(default=None, description="Content summary")
    target_audience_match: Optional[float] = Field(default=None, description="Target audience match score")
    platform_optimization: Optional[Dict[str, Any]] = Field(default=None, description="Platform-specific optimization")
    
    # Suggestions and recommendations
    suggestions: Optional[List[ContentSuggestion]] = Field(default=None, description="Improvement suggestions")
    
    # Metadata
    processing_time: float = Field(..., description="Processing time in seconds")
    confidence_score: float = Field(..., description="Overall analysis confidence")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class {{agent_name}}Agent(BaseAIAgent):
    """{{agent_description}} with comprehensive content understanding capabilities"""
    
    def __init__(
        self,
        agent_id -> None: str,
        model_configs -> None: Dict[str, Dict[str, Any]],
        enable_deep_analysis -> None: bool = True,
        cache_size -> None: int = 1000,
        **kwargs
    ) -> None:
        super().__init__(agent_id=agent_id, **kwargs)
        self.model_configs = model_configs
        self.enable_deep_analysis = enable_deep_analysis
        self.cache_size = cache_size
        
        # Initialize components
        self.model_manager = ContentAnalysisModelManager()
        self.text_preprocessor = TextPreprocessor()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.topic_modeler = TopicModeling()
        self.entity_extractor = EntityExtractor()
        self.visual_analyzer = VisualContentAnalyzer()
        self.audio_analyzer = AudioContentAnalyzer()
        self.metrics_collector = ContentMetricsCollector()
        
        # Load language models
        self._load_models()
        
        # Initialize NLP pipeline
        self._initialize_nlp_pipeline()
        
        logger.info(f"ContentAnalysisAgent {agent_id} initialized")
    
    def _load_models(self) -> None:
        """Load content analysis models"""
        try:
            # Load sentiment analysis model
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_configs.get("sentiment_model", "cardiffnlp/twitter-roberta-base-sentiment-latest")
            )
            
            # Load emotion analysis model
            self.emotion_pipeline = pipeline(
                "text-classification",
                model=self.model_configs.get("emotion_model", "j-hartmann/emotion-english-distilroberta-base")
            )
            
            # Load toxicity detection model
            self.toxicity_pipeline = pipeline(
                "text-classification",
                model=self.model_configs.get("toxicity_model", "unitary/toxic-bert")
            )
            
            logger.info("Content analysis models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise ContentAnalysisException(f"Model loading failed: {e}")
    
    def _initialize_nlp_pipeline(self) -> None:
        """Initialize spaCy NLP pipeline"""
        try:
            # Load spaCy model for entity extraction
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("NLP pipeline initialized successfully")
        except OSError:
            logger.warning("spaCy model not found. Please install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    async def analyze_content(self, task: ContentAnalysisTask) -> ContentAnalysisResult:
        """Analyze content based on specified analysis types"""
        start_time = datetime.utcnow()
        
        try:
            # Initialize result
            result_data = {
                "task_id": task.id,
                "success": True,
                "content_type": task.content_type,
                "confidence_score": 0.0
            }
            
            # Extract text content based on content type
            text_content = await self._extract_text_content(task.content_data, task.content_type)
            
            # Detect language if not specified
            if not task.language and text_content:
                try:
                    result_data["language"] = detect(text_content)
                except:
                    result_data["language"] = "unknown"
            else:
                result_data["language"] = task.language
            
            # Perform requested analyses
            analysis_results = {}
            confidence_scores = []
            
            for analysis_type in task.analysis_types:
                analysis_result = await self._perform_analysis(
                    text_content,
                    analysis_type,
                    task
                )
                analysis_results[analysis_type.value] = analysis_result
                
                if "confidence" in analysis_result:
                    confidence_scores.append(analysis_result["confidence"])
            
            # Process analysis results
            await self._process_analysis_results(analysis_results, result_data, task)
            
            # Calculate overall confidence
            if confidence_scores:
                result_data["confidence_score"] = sum(confidence_scores) / len(confidence_scores)
            else:
                result_data["confidence_score"] = 0.5
            
            # Generate suggestions if requested
            if task.include_suggestions:
                result_data["suggestions"] = await self._generate_suggestions(
                    text_content, analysis_results, task
                )
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result_data["processing_time"] = processing_time
            
            # Create result
            result = ContentAnalysisResult(**result_data)
            
            # Collect metrics
            await self.metrics_collector.record_analysis_completion(
                content_type=task.content_type.value,
                analysis_types=[at.value for at in task.analysis_types],
                processing_time=processing_time,
                success=True
            )
            
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Content analysis task {task.id} failed: {e}")
            
            # Collect error metrics
            await self.metrics_collector.record_analysis_completion(
                content_type=task.content_type.value,
                analysis_types=[at.value for at in task.analysis_types],
                processing_time=processing_time,
                success=False
            )
            
            return ContentAnalysisResult(
                task_id=task.id,
                success=False,
                content_type=task.content_type,
                processing_time=processing_time,
                confidence_score=0.0,
                error_message=str(e)
            )
    
    async def _extract_text_content(self, content_data: Any, content_type: ContentType) -> str:
        """Extract text content based on content type"""
        if content_type == ContentType.TEXT:
            return str(content_data)
        
        elif content_type == ContentType.IMAGE:
            # Use OCR to extract text from image
            return await self.visual_analyzer.extract_text(content_data)
        
        elif content_type == ContentType.VIDEO:
            # Extract text from video (captions, OCR on frames)
            return await self.visual_analyzer.extract_video_text(content_data)
        
        elif content_type == ContentType.AUDIO:
            # Transcribe audio to text
            return await self.audio_analyzer.transcribe(content_data)
        
        elif content_type == ContentType.DOCUMENT:
            # Extract text from document (PDF, DOCX, etc.)
            return await self._extract_document_text(content_data)
        
        elif content_type == ContentType.MIXED_MEDIA:
            # Handle mixed media content
            return await self._extract_mixed_media_text(content_data)
        
        return ""
    
    async def _perform_analysis(
        self, 
        text_content: str, 
        analysis_type: AnalysisType,
        task: ContentAnalysisTask
    ) -> Dict[str, Any]:
        """Perform specific type of analysis"""
        
        if analysis_type == AnalysisType.SENTIMENT:
            return await self._analyze_sentiment(text_content)
        
        elif analysis_type == AnalysisType.TOPIC_MODELING:
            return await self._analyze_topics(text_content, task)
        
        elif analysis_type == AnalysisType.ENTITY_EXTRACTION:
            return await self._extract_entities(text_content)
        
        elif analysis_type == AnalysisType.LANGUAGE_DETECTION:
            return await self._detect_language(text_content)
        
        elif analysis_type == AnalysisType.READABILITY:
            return await self._analyze_readability(text_content)
        
        elif analysis_type == AnalysisType.CONTENT_QUALITY:
            return await self._analyze_content_quality(text_content, task)
        
        elif analysis_type == AnalysisType.PLAGIARISM:
            return await self._check_plagiarism(text_content)
        
        elif analysis_type == AnalysisType.TOXICITY:
            return await self._analyze_toxicity(text_content)
        
        elif analysis_type == AnalysisType.ENGAGEMENT_PREDICTION:
            return await self._predict_engagement(text_content, task)
        
        elif analysis_type == AnalysisType.TREND_ANALYSIS:
            return await self._analyze_trends(text_content, task)
        
        elif analysis_type == AnalysisType.BRAND_SAFETY:
            return await self._check_brand_safety(text_content)
        
        elif analysis_type == AnalysisType.COPYRIGHT_CHECK:
            return await self._check_copyright(text_content)
        
        return {"error": f"Unknown analysis type: {analysis_type}"}
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        try:
            # Basic sentiment analysis
            sentiment_result = self.sentiment_pipeline(text)[0]
            
            # Emotion analysis
            emotion_result = self.emotion_pipeline(text)[0]
            
            return {
                "sentiment": {
                    "label": sentiment_result["label"],
                    "score": sentiment_result["score"]
                },
                "emotion": {
                    "label": emotion_result["label"],
                    "score": emotion_result["score"]
                },
                "confidence": (sentiment_result["score"] + emotion_result["score"]) / 2
            }
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _analyze_topics(self, text: str, task: ContentAnalysisTask) -> Dict[str, Any]:
        """Analyze topics in text"""
        try:
            topics = await self.topic_modeler.extract_topics(
                text=text,
                num_topics=5,
                deep_analysis=task.deep_analysis
            )
            
            return {
                "topics": topics,
                "confidence": 0.8
            }
        except Exception as e:
            logger.error(f"Topic analysis failed: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from text"""
        try:
            if not self.nlp:
                return {"error": "NLP model not available", "confidence": 0.0}
            
            doc = self.nlp(text)
            entities = []
            
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start_pos": ent.start_char,
                    "end_pos": ent.end_char,
                    "confidence": 0.9  # spaCy doesn't provide confidence scores
                })
            
            return {
                "entities": entities,
                "confidence": 0.9
            }
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language of text"""
        try:
            language = detect(text)
            return {
                "language": language,
                "confidence": 0.95
            }
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """Analyze text readability"""
        try:
            flesch_score = flesch_reading_ease(text)
            fk_grade = flesch_kincaid_grade(text)
            
            return {
                "flesch_reading_ease": flesch_score,
                "flesch_kincaid_grade": fk_grade,
                "readability_level": self._get_readability_level(flesch_score),
                "confidence": 0.9
            }
        except Exception as e:
            logger.error(f"Readability analysis failed: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _analyze_content_quality(self, text: str, task: ContentAnalysisTask) -> Dict[str, Any]:
        """Analyze overall content quality"""
        try:
            # Calculate various quality metrics
            readability_score = flesch_reading_ease(text)
            word_count = len(text.split())
            sentence_count = len(re.split(r'[.!?]+', text))
            
            # Grammar score (simplified)
            grammar_score = self._calculate_grammar_score(text)
            
            # Uniqueness score (simplified hash-based)
            uniqueness_score = self._calculate_uniqueness_score(text)
            
            # SEO score
            seo_score = self._calculate_seo_score(text, task)
            
            quality_metrics = {
                "readability_score": max(0, min(100, readability_score)),
                "grammar_score": grammar_score,
                "uniqueness_score": uniqueness_score,
                "engagement_potential": self._predict_engagement_potential(text),
                "seo_score": seo_score,
                "brand_safety_score": 0.9,  # Will be updated by brand safety analysis
                "word_count": word_count,
                "sentence_count": sentence_count
            }
            
            return {
                "quality_metrics": quality_metrics,
                "confidence": 0.8
            }
        except Exception as e:
            logger.error(f"Content quality analysis failed: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _analyze_toxicity(self, text: str) -> Dict[str, Any]:
        """Analyze text toxicity"""
        try:
            toxicity_result = self.toxicity_pipeline(text)[0]
            
            return {
                "toxicity_score": toxicity_result["score"] if toxicity_result["label"] == "TOXIC" else 1 - toxicity_result["score"],
                "is_toxic": toxicity_result["label"] == "TOXIC",
                "confidence": toxicity_result["score"]
            }
        except Exception as e:
            logger.error(f"Toxicity analysis failed: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _check_brand_safety(self, text: str) -> Dict[str, Any]:
        """Check brand safety issues"""
        try:
            # Simplified brand safety check
            unsafe_keywords = ["violence", "hate", "drugs", "alcohol", "gambling"]
            issues = []
            
            text_lower = text.lower()
            for keyword in unsafe_keywords:
                if keyword in text_lower:
                    issues.append(f"Contains {keyword}-related content")
            
            safety_score = 1.0 - (len(issues) * 0.2)
            
            return {
                "brand_safety_score": max(0, safety_score),
                "safety_issues": issues,
                "is_brand_safe": len(issues) == 0,
                "confidence": 0.7
            }
        except Exception as e:
            logger.error(f"Brand safety check failed: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _check_copyright(self, text: str) -> Dict[str, Any]:
        """Check for potential copyright issues"""
        try:
            # Simplified copyright check
            copyright_indicators = ["copyright", "# [EMOJI_REMOVED]", "all rights reserved", "proprietary"]
            warnings = []
            
            text_lower = text.lower()
            for indicator in copyright_indicators:
                if indicator in text_lower:
                    warnings.append(f"Contains copyright indicator: {indicator}")
            
            return {
                "copyright_warnings": warnings,
                "potential_issues": len(warnings) > 0,
                "confidence": 0.6
            }
        except Exception as e:
            logger.error(f"Copyright check failed: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _predict_engagement(self, text: str, task: ContentAnalysisTask) -> Dict[str, Any]:
        """Predict content engagement potential"""
        try:
            # Simplified engagement prediction
            engagement_score = self._predict_engagement_potential(text)
            
            # Adjust based on platform context
            if task.platform_context:
                engagement_score = self._adjust_for_platform(engagement_score, task.platform_context)
            
            return {
                "engagement_prediction": engagement_score,
                "engagement_factors": self._get_engagement_factors(text),
                "confidence": 0.7
            }
        except Exception as e:
            logger.error(f"Engagement prediction failed: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _analyze_trends(self, text: str, task: ContentAnalysisTask) -> Dict[str, Any]:
        """Analyze content trends"""
        try:
            # Extract trending keywords/hashtags
            trending_elements = self._extract_trending_elements(text)
            
            return {
                "trending_keywords": trending_elements["keywords"],
                "hashtags": trending_elements["hashtags"],
                "trend_alignment_score": 0.6,
                "confidence": 0.6
            }
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _check_plagiarism(self, text: str) -> Dict[str, Any]:
        """Check for potential plagiarism"""
        try:
            # Simplified plagiarism check using hash-based similarity
            text_hash = hashlib.md5(text.encode()).hexdigest()
            
            # In a real implementation, this would check against a database
            plagiarism_score = 0.1  # Placeholder
            
            return {
                "plagiarism_score": plagiarism_score,
                "is_likely_plagiarized": plagiarism_score > 0.7,
                "text_hash": text_hash,
                "confidence": 0.5
            }
        except Exception as e:
            logger.error(f"Plagiarism check failed: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _process_analysis_results(
        self, 
        analysis_results -> None: Dict[str, Any], 
        result_data -> None: Dict[str, Any],
        task -> None: ContentAnalysisTask
    ) -> None:
        """Process and aggregate analysis results"""
        
        # Process sentiment results
        if "sentiment" in analysis_results:
            sentiment_data = analysis_results["sentiment"]
            if "sentiment" in sentiment_data:
                result_data["sentiment"] = sentiment_data["sentiment"]
            if "emotion" in sentiment_data:
                result_data["emotion_scores"] = {sentiment_data["emotion"]["label"]: sentiment_data["emotion"]["score"]}
        
        # Process topic results
        if "topic_modeling" in analysis_results:
            topic_data = analysis_results["topic_modeling"]
            if "topics" in topic_data:
                result_data["topics"] = [
                    ContentTopic(
                        topic_id=f"topic_{i}",
                        topic_name=topic.get("name", f"Topic {i}"),
                        keywords=topic.get("keywords", []),
                        probability=topic.get("probability", 0.0),
                        relevance_score=topic.get("relevance", 0.0)
                    ) for i, topic in enumerate(topic_data["topics"])
                ]
        
        # Process entity results
        if "entity_extraction" in analysis_results:
            entity_data = analysis_results["entity_extraction"]
            if "entities" in entity_data:
                result_data["entities"] = [
                    ContentEntity(
                        text=ent["text"],
                        label=ent["label"],
                        confidence=ent["confidence"],
                        start_pos=ent.get("start_pos"),
                        end_pos=ent.get("end_pos")
                    ) for ent in entity_data["entities"]
                ]
        
        # Process quality metrics
        if "content_quality" in analysis_results:
            quality_data = analysis_results["content_quality"]
            if "quality_metrics" in quality_data:
                qm = quality_data["quality_metrics"]
                result_data["quality_metrics"] = ContentQualityMetrics(
                    readability_score=qm.get("readability_score", 50.0),
                    grammar_score=qm.get("grammar_score", 0.8),
                    uniqueness_score=qm.get("uniqueness_score", 0.8),
                    engagement_potential=qm.get("engagement_potential", 0.5),
                    seo_score=qm.get("seo_score", 0.5),
                    brand_safety_score=qm.get("brand_safety_score", 0.9)
                )
        
        # Process toxicity results
        if "toxicity" in analysis_results:
            toxicity_data = analysis_results["toxicity"]
            if "toxicity_score" in toxicity_data:
                result_data["toxicity_score"] = toxicity_data["toxicity_score"]
        
        # Process brand safety results
        if "brand_safety" in analysis_results:
            safety_data = analysis_results["brand_safety"]
            if "safety_issues" in safety_data:
                result_data["brand_safety_issues"] = safety_data["safety_issues"]
        
        # Process copyright results
        if "copyright_check" in analysis_results:
            copyright_data = analysis_results["copyright_check"]
            if "copyright_warnings" in copyright_data:
                result_data["copyright_warnings"] = copyright_data["copyright_warnings"]
    
    async def _generate_suggestions(
        self, 
        text_content: str, 
        analysis_results: Dict[str, Any],
        task: ContentAnalysisTask
    ) -> List[ContentSuggestion]:
        """Generate content improvement suggestions"""
        suggestions = []
        
        # Readability suggestions
        if "readability" in analysis_results:
            readability_data = analysis_results["readability"]
            if readability_data.get("flesch_reading_ease", 50) < 30:
                suggestions.append(ContentSuggestion(
                    category="readability",
                    suggestion="Consider simplifying sentences to improve readability",
                    impact="medium",
                    implementation_effort="low"
                ))
        
        # SEO suggestions
        word_count = len(text_content.split())
        if word_count < 300:
            suggestions.append(ContentSuggestion(
                category="seo",
                suggestion="Consider expanding content to at least 300 words for better SEO",
                impact="high",
                implementation_effort="medium"
            ))
        
        # Engagement suggestions
        if "engagement_prediction" in analysis_results:
            engagement_data = analysis_results["engagement_prediction"]
            if engagement_data.get("engagement_prediction", 0.5) < 0.4:
                suggestions.append(ContentSuggestion(
                    category="engagement",
                    suggestion="Add more interactive elements or call-to-actions to boost engagement",
                    impact="high",
                    implementation_effort="medium"
                ))
        
        # Brand safety suggestions
        if "brand_safety" in analysis_results:
            safety_data = analysis_results["brand_safety"]
            if safety_data.get("safety_issues"):
                suggestions.append(ContentSuggestion(
                    category="brand_safety",
                    suggestion="Review and address brand safety concerns before publishing",
                    impact="high",
                    implementation_effort="low"
                ))
        
        return suggestions
    
    # Helper methods
    def _get_readability_level(self, flesch_score: float) -> str:
        """Get readability level description"""
        if flesch_score >= 90:
            return "Very Easy"
        elif flesch_score >= 80:
            return "Easy"
        elif flesch_score >= 70:
            return "Fairly Easy"
        elif flesch_score >= 60:
            return "Standard"
        elif flesch_score >= 50:
            return "Fairly Difficult"
        elif flesch_score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def _calculate_grammar_score(self, text: str) -> float:
        """Calculate grammar score (simplified)"""
        # Simplified grammar scoring
        # In a real implementation, use grammar checking libraries
        return 0.85
    
    def _calculate_uniqueness_score(self, text: str) -> float:
        """Calculate content uniqueness score"""
        # Simplified uniqueness calculation
        # In a real implementation, compare against known content database
        return 0.9
    
    def _calculate_seo_score(self, text: str, task: ContentAnalysisTask) -> float:
        """Calculate SEO optimization score"""
        score = 0.5
        
        # Check word count
        word_count = len(text.split())
        if 300 <= word_count <= 2000:
            score += 0.2
        
        # Check for headings (simplified)
        if any(line.strip().isupper() for line in text.split('\n')):
            score += 0.1
        
        # Check for keywords (simplified)
        if task.target_audience:
            # In a real implementation, check for relevant keywords
            score += 0.2
        
        return min(1.0, score)
    
    def _predict_engagement_potential(self, text: str) -> float:
        """Predict engagement potential (simplified)"""
        score = 0.5
        
        # Check for questions
        if '?' in text:
            score += 0.1
        
        # Check for emotional words
        emotional_words = ['amazing', 'incredible', 'love', 'hate', 'excited', 'frustrated']
        for word in emotional_words:
            if word.lower() in text.lower():
                score += 0.05
                break
        
        # Check for call-to-actions
        cta_phrases = ['click', 'share', 'comment', 'like', 'subscribe', 'follow']
        for phrase in cta_phrases:
            if phrase.lower() in text.lower():
                score += 0.1
                break
        
        return min(1.0, score)
    
    def _adjust_for_platform(self, score: float, platform: str) -> float:
        """Adjust engagement score for specific platform"""
        # Platform-specific adjustments
        platform_multipliers = {
            "instagram": 1.1,
            "tiktok": 1.2,
            "youtube": 1.0,
            "twitter": 1.05,
            "linkedin": 0.9
        }
        
        multiplier = platform_multipliers.get(platform.lower(), 1.0)
        return min(1.0, score * multiplier)
    
    def _get_engagement_factors(self, text: str) -> List[str]:
        """Get factors that influence engagement"""
        factors = []
        
        if '?' in text:
            factors.append("Contains questions")
        if '!' in text:
            factors.append("Contains exclamations")
        if len(text.split()) < 50:
            factors.append("Concise length")
        if any(word in text.lower() for word in ['tips', 'how', 'guide', 'tutorial']):
            factors.append("Educational content")
        
        return factors
    
    def _extract_trending_elements(self, text: str) -> Dict[str, List[str]]:
        """Extract trending keywords and hashtags"""
        # Extract hashtags
        hashtags = re.findall(r'#\w+', text)
        
        # Extract potential trending keywords (simplified)
        trending_keywords = []
        words = text.lower().split()
        trend_indicators = ['viral', 'trending', 'popular', 'hot', 'new', 'latest']
        for word in words:
            if word in trend_indicators:
                trending_keywords.append(word)
        
        return {
            "hashtags": hashtags,
            "keywords": trending_keywords
        }
    
    async def _extract_document_text(self, content_data: Any) -> str:
        """Extract text from document content"""
        # Placeholder for document text extraction
        # In a real implementation, use libraries like PyPDF2, python-docx, etc.
        return "Extracted document text"
    
    async def _extract_mixed_media_text(self, content_data: Any) -> str:
        """Extract text from mixed media content"""
        # Placeholder for mixed media text extraction
        return "Extracted mixed media text"
    
    async def get_analysis_capabilities(self) -> Dict[str, List[str]]:
        """Get available analysis capabilities"""
        return {
            "content_types": [ct.value for ct in ContentType],
            "analysis_types": [at.value for at in AnalysisType],
            "supported_languages": ["en", "es", "fr", "de", "it", "pt"],
            "features": [
                "Real-time analysis",
                "Batch processing",
                "Multi-language support",
                "Platform optimization",
                "Brand safety checking",
                "Engagement prediction",
                "Quality scoring",
                "Improvement suggestions"
            ]
        }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the content analysis agent"""
        return await self.metrics_collector.get_metrics_summary()


# Template usage example
def create_content_analysis_agent_example() -> None:
    """Example of how to create and use a content analysis agent"""
    
    # Define model configurations
    model_configs = {
        "sentiment_model": "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "emotion_model": "j-hartmann/emotion-english-distilroberta-base",
        "toxicity_model": "unitary/toxic-bert"
    }
    
    # Create agent
    content_agent = ContentAnalysisAgent(
        agent_id="content_analysis_001",
        model_configs=model_configs,
        enable_deep_analysis=True
    )
    
    return content_agent


# Template configuration for code generation
TEMPLATE_CONFIG = {
    "template_name": "content_analysis_agent_template",
    "template_version": "1.0.0",
    "template_description": "Comprehensive content analysis agent for text, media, and mixed content",
    "required_parameters": [
        "agent_name",
        "agent_description",
        "author_name", 
        "author_email",
        "created_date"
    ],
    "optional_parameters": [
        "custom_model_configs",
        "additional_analysis_types",
        "platform_specific_optimizations"
    ],
    "dependencies": [
        "transformers>=4.35.0",
        "spacy>=3.7.0",
        "langdetect>=1.0.9",
        "textstat>=0.7.0",
        "numpy>=1.24.0",
        "torch>=2.0.0"
    ],
    "features": [
        "Multi-content type analysis",
        "Sentiment and emotion analysis",
        "Topic modeling and entity extraction",
        "Content quality assessment",
        "Brand safety checking",
        "Plagiarism detection",
        "Engagement prediction",
        "Platform optimization",
        "Improvement suggestions",
        "Performance monitoring"
    ]
}

# File has syntax issues - needs manual review