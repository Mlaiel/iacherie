"""
Text Agent - Industrial AI-Powered Text Processing System

Advanced enterprise-grade text analysis, processing, and generation system for content creators.
Provides comprehensive text fingerprinting, sentiment analysis, language processing, and intelligent content generation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  IMPORTANT LEGAL NOTICE:
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
import hashlib
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import re
import nltk
import spacy
import openai
from transformers import pipeline, AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import textstat
from langdetect import detect, DetectorFactory

from ..base import BaseAgent, AgentStatus, AgentCapability
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
try:
    from core.exceptions import ValidationError, ProcessingError, SecurityError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ValidationError, ProcessingError, SecurityError = globals().get('ValidationError, ProcessingError, SecurityError', Exception)
from ...security.content_protection import ContentProtector
from ...utils.performance_monitor import PerformanceMonitor
from ...models.text_content import TextContent, TextAnalysis, ContentFingerprint

# Ensure consistent language detection
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

class TextProcessingType(Enum):
    """Text processing operation types"""
    ANALYSIS = "analysis"
    GENERATION = "generation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    SENTIMENT = "sentiment"
    EXTRACTION = "extraction"
    CLASSIFICATION = "classification"
    FINGERPRINTING = "fingerprinting"

class TextQuality(Enum):
    """Text quality assessment levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    CRITICAL = "critical"

@dataclass
class TextProcessingConfig:
    """Configuration for text processing operations"""
    max_length: int = 10000
    min_length: int = 10
    enable_preprocessing: bool = True
    enable_sentiment_analysis: bool = True
    enable_entity_extraction: bool = True
    enable_topic_modeling: bool = True
    enable_quality_assessment: bool = True
    languages_supported: List[str] = field(default_factory=lambda: ['en', 'fr', 'de', 'es', 'it'])
    similarity_threshold: float = 0.85
    fingerprint_algorithm: str = "sha256"

@dataclass
class TextAnalysisResult:
    """Comprehensive text analysis results"""
    text_id: str
    language: str
    language_confidence: float
    word_count: int
    character_count: int
    sentence_count: int
    paragraph_count: int
    readability_score: float
    sentiment_score: float
    sentiment_label: str
    entities: List[Dict[str, Any]]
    topics: List[Dict[str, Any]]
    keywords: List[str]
    fingerprint: str
    quality_score: float
    quality_level: TextQuality
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class TextAgent(BaseAgent):
    """
    Industrial-grade AI Text Processing Agent
    
    Provides comprehensive text analysis, processing, and generation capabilities
    for content creators with enterprise-level performance and security.
    """
    
    def __init__(self, config: Optional[TextProcessingConfig] = None):
        super().__init__(
            agent_type="text_agent",
            capabilities=[
                AgentCapability.CONTENT_ANALYSIS,
                AgentCapability.CONTENT_GENERATION,
                AgentCapability.FINGERPRINTING,
                AgentCapability.MONITORING
            ]
        )
        
        self.config = config or TextProcessingConfig()
        self.content_protector = ContentProtector()
        self.performance_monitor = PerformanceMonitor("text_agent")
        
        # Initialize NLP models
        self._init_nlp_models()
        
        # Text processing statistics
        self.processing_stats = {
            "texts_processed": 0,
            "total_words_analyzed": 0,
            "average_processing_time": 0.0,
            "fingerprints_generated": 0,
            "sentiments_analyzed": 0
        }
        
        logger.info(f"TextAgent initialized with config: {self.config}")
    
    def _init_nlp_models(self):
        """Initialize NLP models and pipelines"""



        try:
            # Load spaCy models for different languages
            self.nlp_models = {}
            language_models = {
                'en': 'en_core_web_sm',
                'fr': 'fr_core_news_sm', 
                'de': 'de_core_news_sm',
                'es': 'es_core_news_sm',
                'it': 'it_core_news_sm'
            }
            
            for lang, model_name in language_models.items():
                try:
                    self.nlp_models[lang] = spacy.load(model_name)
                except OSError:
                    logger.warning(f"SpaCy model {model_name} not found for {lang}")
                    self.nlp_models[lang] = spacy.load('en_core_web_sm')  # Fallback
            
            # Initialize sentence transformer for embeddings
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize sentiment analysis pipeline
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Initialize text generation pipeline
            self.text_generator = pipeline(
                "text-generation",
                model="gpt2-medium",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Initialize TF-IDF vectorizer for keyword extraction
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 3)
            )
            
            logger.info("NLP models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing NLP models: {e}")
            raise ProcessingError(f"Failed to initialize NLP models: {e}")
    
    async def process_text(
        self,
        text: str,
        processing_type: TextProcessingType = TextProcessingType.ANALYSIS,
        options: Optional[Dict[str, Any]] = None
    ) -> TextAnalysisResult:
        """
        Process text with comprehensive analysis and protection
        
        Args:
            text: Input text to process
            processing_type: Type of processing to perform
            options: Additional processing options
            
        Returns:
            TextAnalysisResult: Comprehensive analysis results
        """
        start_time = time.time()
        text_id = str(uuid.uuid4())
        
        try:
            # Validate input
            await self._validate_text_input(text)
            
            # Clean and preprocess text
            if self.config.enable_preprocessing:
                text = await self._preprocess_text(text)
            
            # Detect language
            language, lang_confidence = await self._detect_language(text)
            
            # Basic text statistics
            stats = await self._calculate_text_statistics(text)
            
            # Generate content fingerprint
            fingerprint = await self._generate_fingerprint(text)
            
            # Sentiment analysis
            sentiment_score, sentiment_label = await self._analyze_sentiment(text)
            
            # Entity extraction
            entities = await self._extract_entities(text, language)
            
            # Topic modeling and keyword extraction
            topics = await self._extract_topics(text)
            keywords = await self._extract_keywords(text)
            
            # Quality assessment
            quality_score, quality_level = await self._assess_text_quality(text)
            
            # Readability analysis
            readability_score = await self._calculate_readability(text)
            
            processing_time = time.time() - start_time
            
            # Create analysis result
            result = TextAnalysisResult(
                text_id=text_id,
                language=language,
                language_confidence=lang_confidence,
                word_count=stats['word_count'],
                character_count=stats['character_count'],
                sentence_count=stats['sentence_count'],
                paragraph_count=stats['paragraph_count'],
                readability_score=readability_score,
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label,
                entities=entities,
                topics=topics,
                keywords=keywords,
                fingerprint=fingerprint,
                quality_score=quality_score,
                quality_level=quality_level,
                processing_time=processing_time,
                metadata={
                    'processing_type': processing_type.value,
                    'options': options or {},
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'agent_version': self.version
                }
            )
            
            # Store analysis results
            await self._store_analysis_results(result, text)
            
            # Update statistics
            self._update_processing_stats(result)
            
            # Log successful processing
            logger.info(f"Text processed successfully: {text_id} ({processing_time:.2f}s)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing text {text_id}: {e}")
            raise ProcessingError(f"Text processing failed: {e}")
    
    async def generate_content(
        self,
        prompt: str,
        max_length: int = 200,
        temperature: float = 0.7,
        style: Optional[str] = None,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Generate AI-powered text content
        
        Args:
            prompt: Generation prompt
            max_length: Maximum generated text length
            temperature: Generation randomness (0.0 to 1.0)
            style: Writing style (formal, casual, creative, etc.)
            language: Target language for generation
            
        Returns:
            Dict containing generated content and metadata
        """
        start_time = time.time()
        generation_id = str(uuid.uuid4())
        
        try:
            # Validate prompt
            if not prompt or len(prompt.strip()) < 5:
                raise ValidationError("Generation prompt too short")
            
            # Apply style modifications to prompt
            if style:
                prompt = await self._apply_style_to_prompt(prompt, style)
            
            # Generate content using transformer model
            generated_outputs = self.text_generator(
                prompt,
                max_length=max_length,
                temperature=temperature,
                num_return_sequences=1,
                do_sample=True,
                pad_token_id=self.text_generator.tokenizer.eos_token_id
            )
            
            generated_text = generated_outputs[0]['generated_text']
            
            # Clean and post-process generated text
            generated_text = await self._post_process_generated_text(generated_text, prompt)
            
            # Analyze generated content
            analysis = await self.process_text(generated_text, TextProcessingType.ANALYSIS)
            
            generation_time = time.time() - start_time
            
            result = {
                'generation_id': generation_id,
                'prompt': prompt,
                'generated_text': generated_text,
                'analysis': analysis,
                'metadata': {
                    'max_length': max_length,
                    'temperature': temperature,
                    'style': style,
                    'language': language,
                    'generation_time': generation_time,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            }
            
            # Store generation results
            await self._store_generation_results(result)
            
            logger.info(f"Content generated successfully: {generation_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise ProcessingError(f"Content generation failed: {e}")
    
    async def detect_plagiarism(
        self,
        text: str,
        reference_texts: Optional[List[str]] = None,
        similarity_threshold: float = None
    ) -> Dict[str, Any]:
        """
        Detect potential plagiarism in text content
        
        Args:
            text: Text to check for plagiarism
            reference_texts: Reference texts to compare against
            similarity_threshold: Minimum similarity for plagiarism detection
            
        Returns:
            Dict containing plagiarism detection results
        """
        threshold = similarity_threshold or self.config.similarity_threshold
        
        try:
            # Generate text embedding
            text_embedding = self.sentence_model.encode([text])
            
            # Get reference embeddings from database or provided texts
            if reference_texts:
                reference_embeddings = self.sentence_model.encode(reference_texts)
            else:
                reference_embeddings = await self._get_reference_embeddings()
            
            if len(reference_embeddings) == 0:
                return {
                    'plagiarism_detected': False,
                    'similarity_scores': [],
                    'max_similarity': 0.0,
                    'suspicious_matches': []
                }
            
            # Calculate cosine similarities
            similarities = cosine_similarity(text_embedding, reference_embeddings)[0]
            
            # Find suspicious matches
            suspicious_matches = []
            for i, similarity in enumerate(similarities):
                if similarity >= threshold:
                    suspicious_matches.append({
                        'index': i,
                        'similarity': float(similarity),
                        'text_preview': reference_texts[i][:100] + "..." if reference_texts and i < len(reference_texts) else "Reference text"
                    })
            
            max_similarity = float(np.max(similarities)) if len(similarities) > 0 else 0.0
            
            result = {
                'plagiarism_detected': max_similarity >= threshold,
                'similarity_scores': similarities.tolist(),
                'max_similarity': max_similarity,
                'suspicious_matches': suspicious_matches,
                'threshold_used': threshold,
                'total_references_checked': len(reference_embeddings)
            }
            
            logger.info(f"Plagiarism check completed: {len(suspicious_matches)} suspicious matches found")
            return result
            
        except Exception as e:
            logger.error(f"Error in plagiarism detection: {e}")
            raise ProcessingError(f"Plagiarism detection failed: {e}")
    
    async def _validate_text_input(self, text: str):
        """Validate text input parameters"""
        if not text or not isinstance(text, str):
            raise ValidationError("Invalid text input: must be non-empty string")
        
        if len(text) > self.config.max_length:
            raise ValidationError(f"Text too long: {len(text)} > {self.config.max_length}")
        
        if len(text) < self.config.min_length:
            raise ValidationError(f"Text too short: {len(text)} < {self.config.min_length}")
    
    async def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove or replace special characters
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\'\"]', ' ', text)
        
        # Normalize quotes and dashes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        text = text.replace('–', '-').replace('—', '-')
        
        return text
    
    async def _detect_language(self, text: str) -> Tuple[str, float]:
        """Detect text language with confidence score"""



        try:
            language = detect(text)
            # Simple confidence estimation based on text length and clarity
            confidence = min(0.9, len(text) / 1000 + 0.5)
            return language, confidence
        except:
            return 'en', 0.5  # Default to English with low confidence
    
    async def _calculate_text_statistics(self, text: str) -> Dict[str, int]:
        """Calculate basic text statistics"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        paragraphs = text.split('\n\n')
        
        return {
            'word_count': len(words),
            'character_count': len(text),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'paragraph_count': len([p for p in paragraphs if p.strip()])
        }
    
    async def _generate_fingerprint(self, text: str) -> str:
        """Generate unique fingerprint for text content"""
        # Normalize text for consistent fingerprinting
        normalized_text = re.sub(r'\s+', ' ', text.lower().strip())
        
        # Generate hash
        if self.config.fingerprint_algorithm == "sha256":
            return hashlib.sha256(normalized_text.encode()).hexdigest()
        elif self.config.fingerprint_algorithm == "md5":
            return hashlib.md5(normalized_text.encode()).hexdigest()
        else:
            return hashlib.sha256(normalized_text.encode()).hexdigest()
    
    async def _analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """Analyze text sentiment"""



        try:
            result = self.sentiment_analyzer(text[:512])  # Limit text length for model
            
            if result and len(result) > 0:
                sentiment_data = result[0]
                label = sentiment_data['label'].lower()
                score = sentiment_data['score']
                
                # Convert to normalized score (-1 to 1)
                if label == 'negative':
                    normalized_score = -score
                elif label == 'positive':
                    normalized_score = score
                else:  # neutral
                    normalized_score = 0.0
                
                return normalized_score, label
            
            return 0.0, 'neutral'
            
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            return 0.0, 'neutral'
    
    async def _extract_entities(self, text: str, language: str) -> List[Dict[str, Any]]:
        """Extract named entities from text"""



        try:
            nlp = self.nlp_models.get(language, self.nlp_models['en'])
            doc = nlp(text[:1000000])  # Limit text length for processing
            
            entities = []
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'description': spacy.explain(ent.label_),
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': 0.9  # SpaCy doesn't provide confidence scores directly
                })
            
            return entities
            
        except Exception as e:
            logger.warning(f"Entity extraction failed: {e}")
            return []
    
    async def _extract_topics(self, text: str) -> List[Dict[str, Any]]:
        """Extract topics from text using TF-IDF"""



        try:
            # Simple topic extraction using TF-IDF
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text])
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Get top scoring terms as topics
            top_indices = np.argsort(tfidf_scores)[::-1][:10]
            
            topics = []
            for i, idx in enumerate(top_indices):
                if tfidf_scores[idx] > 0:
                    topics.append({
                        'term': feature_names[idx],
                        'score': float(tfidf_scores[idx]),
                        'rank': i + 1
                    })
            
            return topics
            
        except Exception as e:
            logger.warning(f"Topic extraction failed: {e}")
            return []
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""



        try:
            # Use TF-IDF to extract important terms
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text])
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            top_indices = np.argsort(tfidf_scores)[::-1][:20]
            keywords = [feature_names[idx] for idx in top_indices if tfidf_scores[idx] > 0]
            
            return keywords
            
        except Exception as e:
            logger.warning(f"Keyword extraction failed: {e}")
            return []
    
    async def _assess_text_quality(self, text: str) -> Tuple[float, TextQuality]:
        """Assess overall text quality"""



        try:
            # Quality metrics
            word_count = len(text.split())
            sentence_count = len(re.split(r'[.!?]+', text))
            avg_words_per_sentence = word_count / max(sentence_count, 1)
            
            # Readability (Flesch reading ease)
            readability = textstat.flesch_reading_ease(text)
            
            # Grammar and spelling check (simplified)
            grammar_score = await self._estimate_grammar_quality(text)
            
            # Combine scores
            quality_score = (
                min(100, readability) * 0.3 +
                min(100, grammar_score * 100) * 0.4 +
                min(100, (avg_words_per_sentence / 20) * 100) * 0.3
            ) / 100
            
            # Determine quality level
            if quality_score >= 0.8:
                quality_level = TextQuality.EXCELLENT
            elif quality_score >= 0.6:
                quality_level = TextQuality.GOOD
            elif quality_score >= 0.4:
                quality_level = TextQuality.AVERAGE
            elif quality_score >= 0.2:
                quality_level = TextQuality.POOR
            else:
                quality_level = TextQuality.CRITICAL
            
            return quality_score, quality_level
            
        except Exception as e:
            logger.warning(f"Quality assessment failed: {e}")
            return 0.5, TextQuality.AVERAGE
    
    async def _calculate_readability(self, text: str) -> float:
        """Calculate text readability score"""



        try:
            return textstat.flesch_reading_ease(text)
        except:
            return 50.0  # Default average readability
    
    async def _estimate_grammar_quality(self, text: str) -> float:
        """Estimate grammar quality (simplified implementation)"""
        # Simplified grammar quality estimation
        # In production, use tools like LanguageTool or Grammarly API
        
        sentences = re.split(r'[.!?]+', text)
        quality_indicators = 0
        total_checks = 0
        
        for sentence in sentences:
            if sentence.strip():
                total_checks += 1
                # Check for proper capitalization
                if sentence.strip()[0].isupper():
                    quality_indicators += 1
                # Check for reasonable length
                if 5 <= len(sentence.split()) <= 25:
                    quality_indicators += 1
        
        return quality_indicators / max(total_checks * 2, 1)
    
    async def _store_analysis_results(self, result: TextAnalysisResult, text: str):
        """Store analysis results in database"""



        try:
            async with get_db_session() as session:
                # Create text content record
                text_content = TextContent(
                    id=result.text_id,
                    content=text,
                    language=result.language,
                    fingerprint=result.fingerprint,
                    created_at=datetime.now(timezone.utc)
                )
                
                # Create analysis record
                analysis = TextAnalysis(
                    text_id=result.text_id,
                    word_count=result.word_count,
                    sentiment_score=result.sentiment_score,
                    sentiment_label=result.sentiment_label,
                    quality_score=result.quality_score,
                    readability_score=result.readability_score,
                    entities=json.dumps(result.entities),
                    topics=json.dumps(result.topics),
                    keywords=json.dumps(result.keywords),
                    metadata=json.dumps(result.metadata),
                    created_at=datetime.now(timezone.utc)
                )
                
                session.add(text_content)
                session.add(analysis)
                await session.commit()
                
        except Exception as e:
            logger.error(f"Error storing analysis results: {e}")
    
    def _update_processing_stats(self, result: TextAnalysisResult):
        """Update processing statistics"""
        self.processing_stats["texts_processed"] += 1
        self.processing_stats["total_words_analyzed"] += result.word_count
        self.processing_stats["fingerprints_generated"] += 1
        self.processing_stats["sentiments_analyzed"] += 1
        
        # Update average processing time
        total_time = (self.processing_stats["average_processing_time"] * 
                     (self.processing_stats["texts_processed"] - 1) + 
                     result.processing_time)
        self.processing_stats["average_processing_time"] = total_time / self.processing_stats["texts_processed"]
    
    async def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent performance statistics"""
        base_stats = await super().get_agent_stats()
        base_stats.update({
            "text_processing": self.processing_stats,
            "models_loaded": len(self.nlp_models),
            "supported_languages": self.config.languages_supported
        })
        return base_stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform agent health check"""
        health_status = await super().health_check()
        
        # Check NLP models
        models_healthy = all(model is not None for model in self.nlp_models.values())
        
        # Check sentence transformer
        sentence_model_healthy = self.sentence_model is not None
        
        health_status.update({
            "nlp_models_healthy": models_healthy,
            "sentence_model_healthy": sentence_model_healthy,
            "total_texts_processed": self.processing_stats["texts_processed"]
        })
        
        return health_status


class TextAgentManager:
    """
    Manager for multiple TextAgent instances with load balancing and orchestration
    """
    
    def __init__(self, num_agents: int = 3):
        self.agents: List[TextAgent] = []
        self.current_agent_index = 0
        
        # Initialize multiple agents for load balancing
        for i in range(num_agents):
            agent = TextAgent()
            self.agents.append(agent)
        
        logger.info(f"TextAgentManager initialized with {num_agents} agents")
    
    def get_next_agent(self) -> TextAgent:
        """Get next available agent using round-robin"""
        agent = self.agents[self.current_agent_index]
        self.current_agent_index = (self.current_agent_index + 1) % len(self.agents)
        return agent
    
    async def process_text_batch(
        self,
        texts: List[str],
        processing_type: TextProcessingType = TextProcessingType.ANALYSIS
    ) -> List[TextAnalysisResult]:
        """Process multiple texts concurrently"""
        tasks = []
        
        for text in texts:
            agent = self.get_next_agent()
            task = agent.process_text(text, processing_type)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log errors
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing text {i}: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def get_aggregate_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics from all agents"""
        agent_stats = await asyncio.gather(*[agent.get_agent_stats() for agent in self.agents])
        
        # Aggregate statistics
        total_texts = sum(stats["text_processing"]["texts_processed"] for stats in agent_stats)
        total_words = sum(stats["text_processing"]["total_words_analyzed"] for stats in agent_stats)
        avg_processing_time = sum(stats["text_processing"]["average_processing_time"] for stats in agent_stats) / len(agent_stats)
        
        return {
            "total_agents": len(self.agents),
            "aggregate_texts_processed": total_texts,
            "aggregate_words_analyzed": total_words,
            "average_processing_time": avg_processing_time,
            "individual_agent_stats": agent_stats
        }
