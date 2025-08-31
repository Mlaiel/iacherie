"""Quality Controller - Enterprise Content Quality Management System

Ultra-advanced quality assurance and validation system for content creation,
ensuring professional standards and brand compliance across all content types.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""import asyncio
import logging
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from collections import Counter

# NLP and quality analysis
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from textstat import (
    flesch_reading_ease, flesch_kincaid_grade,
    automated_readability_index, coleman_liau_index,
    gunning_fog, smog_index
)
import language_tool_python
from spellchecker import SpellChecker
import textdistance

# AI/ML models
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    pipeline, AutoModel
)
import torch
import torch.nn.functional as F

# Image quality analysis
from PIL import Image, ImageStat
import cv2
import numpy as np
from skimage import measure, filters

# Audio quality analysis
import librosa
import scipy.signal

# Database and API
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from fastapi import HTTPException
from pydantic import BaseModel, Field

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
from ...models.content import Content, ContentType, ContentMetadata
from ...models.quality import QualityCheck, QualityMetric, QualityStandard
from ...utils.performance import PerformanceMonitor
from ...ai.llm_engine import UnifiedLLMEngine

logger = logging.getLogger(__name__)
settings = get_settings()


class QualityDimension(str, Enum):
    """Quality assessment dimensions"""    ACCURACY = "accuracy"
    CLARITY = "clarity"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    ENGAGEMENT = "engagement"
    GRAMMAR = "grammar"
    ORIGINALITY = "originality"
    RELEVANCE = "relevance"
    TONE = "tone"
    STRUCTURE = "structure"
    SEO_OPTIMIZATION = "seo_optimization"
    BRAND_ALIGNMENT = "brand_alignment"


class QualityLevel(str, Enum):
    """Quality level standards"""    DRAFT = "draft"
    REVIEW_READY = "review_ready"
    PROFESSIONAL = "professional"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class ContentFormat(str, Enum):
    """Content format types for quality assessment"""    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    MULTIMEDIA = "multimedia"


@dataclass
class QualityMetrics:
    """Comprehensive quality metrics"""    # Overall scores
    overall_score: float = 0.0
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    
    # Text quality metrics
    readability_score: float = 0.0
    grammar_score: float = 0.0
    spelling_score: float = 0.0
    vocabulary_richness: float = 0.0
    sentence_structure_score: float = 0.0
    
    # Content quality metrics
    originality_score: float = 0.0
    factual_accuracy_score: float = 0.0
    brand_alignment_score: float = 0.0
    tone_consistency_score: float = 0.0
    
    # Technical quality metrics (for media)
    technical_quality_score: float = 0.0
    format_compliance_score: float = 0.0
    accessibility_score: float = 0.0
    
    # SEO and engagement metrics
    seo_score: float = 0.0
    engagement_potential_score: float = 0.0
    social_media_optimization_score: float = 0.0
    
    # Detailed analysis
    issues_found: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    quality_warnings: List[str] = field(default_factory=list)


@dataclass
class QualityCriteria:
    """Quality assessment criteria"""    target_quality_level: QualityLevel = QualityLevel.PROFESSIONAL
    required_dimensions: List[QualityDimension] = field(default_factory=list)
    minimum_scores: Dict[str, float] = field(default_factory=dict)
    content_requirements: Dict[str, Any] = field(default_factory=dict)
    brand_guidelines: Dict[str, Any] = field(default_factory=dict)
    seo_requirements: Dict[str, Any] = field(default_factory=dict)
    accessibility_requirements: Dict[str, Any] = field(default_factory=dict)


class QualityController:
    """Enterprise content quality management and validation system"""    
    def __init__(self):
        self.settings = get_settings()
        self.performance_monitor = PerformanceMonitor("quality_controller")
        self.cache_manager = CacheManager("quality_control")
        self.llm_engine = UnifiedLLMEngine()
        
        # Initialize quality analysis tools
        self._initialize_quality_tools()
        
        # Quality standards and thresholds
        self.quality_thresholds = self._initialize_quality_thresholds()
        
        # Quality metrics cache
        self._metrics_cache = {}
        
        # Quality models
        self._quality_models = {}
    
    def _initialize_quality_tools(self):
        """Initialize quality analysis tools and models"""        try:
            # Grammar and spell checking
            self.grammar_tool = language_tool_python.LanguageTool('en-US')
            self.spell_checker = SpellChecker()
            
            # Sentiment and emotion analysis
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            
            # Content classification and quality models
            self.quality_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Toxicity and safety detection
            self.toxicity_detector = pipeline(
                "text-classification",
                model="martin-ha/toxic-comment-model",
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info("Quality analysis tools initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize quality tools: {e}")
            # Initialize minimal fallback tools
            self.grammar_tool = None
            self.spell_checker = SpellChecker()
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
    
    def _initialize_quality_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize quality thresholds for different levels"""        return {
            QualityLevel.DRAFT.value: {
                "overall_score": 0.4,
                "grammar_score": 0.5,
                "readability_score": 30.0,
                "originality_score": 0.3
            },
            QualityLevel.REVIEW_READY.value: {
                "overall_score": 0.6,
                "grammar_score": 0.7,
                "readability_score": 50.0,
                "originality_score": 0.5
            },
            QualityLevel.PROFESSIONAL.value: {
                "overall_score": 0.75,
                "grammar_score": 0.85,
                "readability_score": 60.0,
                "originality_score": 0.7
            },
            QualityLevel.PREMIUM.value: {
                "overall_score": 0.85,
                "grammar_score": 0.9,
                "readability_score": 70.0,
                "originality_score": 0.8
            },
            QualityLevel.ENTERPRISE.value: {
                "overall_score": 0.9,
                "grammar_score": 0.95,
                "readability_score": 75.0,
                "originality_score": 0.9
            }
        }
    
    async def validate_content(
        self,
        content: Dict[str, Any],
        criteria: Dict[str, Any],
        user_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Comprehensive content quality validation"""        
        async with self.performance_monitor.track_operation("content_validation"):
            try:
                validation_id = str(uuid.uuid4())
                
                # Parse quality criteria
                quality_criteria = self._parse_quality_criteria(criteria)
                
                # Determine content format
                content_format = self._determine_content_format(content)
                
                # Perform quality assessment based on format
                quality_metrics = await self._assess_content_quality(
                    content, content_format, quality_criteria
                )
                
                # Generate validation result
                validation_result = await self._generate_validation_result(
                    quality_metrics, quality_criteria, validation_id
                )
                
                # Store quality assessment record
                await self._store_quality_assessment(
                    validation_id, user_id, content, quality_metrics, db
                )
                
                # Generate improvement recommendations
                recommendations = await self._generate_quality_recommendations(
                    quality_metrics, quality_criteria
                )
                
                return {
                    "validation_id": validation_id,
                    "overall_score": quality_metrics.overall_score,
                    "quality_level": self._determine_quality_level(quality_metrics),
                    "passed_checks": validation_result.get("passed_checks", []),
                    "failed_checks": validation_result.get("failed_checks", []),
                    "warnings": quality_metrics.quality_warnings,
                    "detailed_metrics": self._serialize_quality_metrics(quality_metrics),
                    "recommendations": recommendations,
                    "next_steps": validation_result.get("next_steps", []),
                    "validation_timestamp": datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                logger.error(f"Content validation error: {e}")
                raise HTTPException(status_code=500, detail=f"Quality validation failed: {str(e)}")
    
    def _parse_quality_criteria(self, criteria: Dict[str, Any]) -> QualityCriteria:
        """Parse and validate quality criteria"""        
        try:
            return QualityCriteria(
                target_quality_level=QualityLevel(criteria.get("target_level", "professional")),
                required_dimensions=[
                    QualityDimension(dim) for dim in criteria.get("required_dimensions", [])
                ],
                minimum_scores=criteria.get("minimum_scores", {}),
                content_requirements=criteria.get("content_requirements", {}),
                brand_guidelines=criteria.get("brand_guidelines", {}),
                seo_requirements=criteria.get("seo_requirements", {}),
                accessibility_requirements=criteria.get("accessibility_requirements", {})
            )
        except Exception as e:
            logger.error(f"Error parsing quality criteria: {e}")
            return QualityCriteria()
    
    def _determine_content_format(self, content: Dict[str, Any]) -> ContentFormat:
        """Determine content format for appropriate quality assessment"""        
        if "text" in content or "body" in content:
            return ContentFormat.TEXT
        elif "image_data" in content or "image_url" in content:
            return ContentFormat.IMAGE
        elif "audio_data" in content or "audio_url" in content:
            return ContentFormat.AUDIO
        elif "video_data" in content or "video_url" in content:
            return ContentFormat.VIDEO
        elif "file_data" in content:
            return ContentFormat.DOCUMENT
        else:
            return ContentFormat.MULTIMEDIA
    
    async def _assess_content_quality(
        self,
        content: Dict[str, Any],
        content_format: ContentFormat,
        criteria: QualityCriteria
    ) -> QualityMetrics:
        """Perform comprehensive quality assessment"""        
        try:
            if content_format == ContentFormat.TEXT:
                return await self._assess_text_quality(content, criteria)
            elif content_format == ContentFormat.IMAGE:
                return await self._assess_image_quality(content, criteria)
            elif content_format == ContentFormat.AUDIO:
                return await self._assess_audio_quality(content, criteria)
            elif content_format == ContentFormat.VIDEO:
                return await self._assess_video_quality(content, criteria)
            elif content_format == ContentFormat.DOCUMENT:
                return await self._assess_document_quality(content, criteria)
            else:
                return await self._assess_multimedia_quality(content, criteria)
                
        except Exception as e:
            logger.error(f"Quality assessment error: {e}")
            return QualityMetrics()
    
    async def _assess_text_quality(
        self,
        content: Dict[str, Any],
        criteria: QualityCriteria
    ) -> QualityMetrics:
        """Assess text content quality"""        
        text = content.get("text", "") or content.get("body", "")
        if not text:
            return QualityMetrics(issues_found=[{"type": "error", "message": "No text content found"}])
        
        metrics = QualityMetrics()
        
        try:
            # Basic text analysis
            word_count = len(word_tokenize(text))
            sentence_count = len(sent_tokenize(text))
            char_count = len(text)
            
            # Readability analysis
            metrics.readability_score = self._calculate_readability_score(text)
            
            # Grammar and spelling analysis
            if self.grammar_tool:
                grammar_issues = self.grammar_tool.check(text)
                grammar_score = max(0, 1 - (len(grammar_issues) / max(word_count / 10, 1)))
                metrics.grammar_score = grammar_score
                
                # Add grammar issues to detailed analysis
                for issue in grammar_issues[:10]:  # Limit to top 10 issues
                    metrics.issues_found.append({
                        "type": "grammar",
                        "message": issue.message,
                        "context": issue.context,
                        "suggestions": issue.replacements[:3]
                    })
            
            # Spelling analysis
            words = word_tokenize(text.lower())
            misspelled = self.spell_checker.unknown(words)
            spelling_score = 1 - (len(misspelled) / max(len(words), 1))
            metrics.spelling_score = spelling_score
            
            if misspelled:
                metrics.issues_found.append({
                    "type": "spelling",
                    "message": f"Found {len(misspelled)} misspelled words",
                    "misspelled_words": list(misspelled)[:10]
                })
            
            # Vocabulary richness
            unique_words = len(set(words))
            metrics.vocabulary_richness = unique_words / max(len(words), 1)
            
            # Sentence structure analysis
            metrics.sentence_structure_score = self._analyze_sentence_structure(text)
            
            # Content quality analysis
            metrics.originality_score = await self._assess_originality(text)
            metrics.tone_consistency_score = self._assess_tone_consistency(text)
            metrics.engagement_potential_score = self._assess_engagement_potential(text)
            
            # SEO analysis if requested
            if criteria.seo_requirements:
                metrics.seo_score = self._assess_seo_quality(text, criteria.seo_requirements)
            
            # Brand alignment if guidelines provided
            if criteria.brand_guidelines:
                metrics.brand_alignment_score = await self._assess_brand_alignment(
                    text, criteria.brand_guidelines
                )
            
            # Calculate dimension scores
            metrics.dimension_scores = {
                QualityDimension.ACCURACY.value: metrics.factual_accuracy_score,
                QualityDimension.CLARITY.value: metrics.readability_score / 100,
                QualityDimension.GRAMMAR.value: metrics.grammar_score,
                QualityDimension.ORIGINALITY.value: metrics.originality_score,
                QualityDimension.ENGAGEMENT.value: metrics.engagement_potential_score,
                QualityDimension.TONE.value: metrics.tone_consistency_score,
                QualityDimension.STRUCTURE.value: metrics.sentence_structure_score
            }
            
            # Calculate overall score
            metrics.overall_score = self._calculate_overall_score(metrics)
            
            # Generate quality warnings
            metrics.quality_warnings = self._generate_quality_warnings(metrics, criteria)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Text quality assessment error: {e}")
            metrics.issues_found.append({
                "type": "error",
                "message": f"Quality assessment failed: {str(e)}"
            })
            return metrics
    
    def _calculate_readability_score(self, text: str) -> float:
        """Calculate comprehensive readability score"""        
        try:
            # Multiple readability metrics
            flesch_ease = flesch_reading_ease(text)
            flesch_kincaid = flesch_kincaid_grade(text)
            coleman_liau = coleman_liau_index(text)
            
            # Normalize and average
            normalized_flesch = max(0, min(100, flesch_ease))
            normalized_fk = max(0, min(18, flesch_kincaid)) / 18 * 100
            normalized_cl = max(0, min(18, coleman_liau)) / 18 * 100
            
            return (normalized_flesch + normalized_fk + normalized_cl) / 3
            
        except Exception as e:
            logger.error(f"Readability calculation error: {e}")
            return 50.0  # Default middle score
    
    def _analyze_sentence_structure(self, text: str) -> float:
        """Analyze sentence structure quality"""        
        try:
            sentences = sent_tokenize(text)
            if not sentences:
                return 0.0
            
            # Analyze sentence length variation
            sentence_lengths = [len(word_tokenize(sent)) for sent in sentences]
            avg_length = np.mean(sentence_lengths)
            length_std = np.std(sentence_lengths)
            
            # Good structure has varied sentence lengths (not all short or all long)
            ideal_avg_length = 15  # Words per sentence
            ideal_variation = 5    # Standard deviation
            
            length_score = 1 - abs(avg_length - ideal_avg_length) / ideal_avg_length
            variation_score = 1 - abs(length_std - ideal_variation) / ideal_variation
            
            # Check for run-on sentences (> 30 words)
            run_on_sentences = sum(1 for length in sentence_lengths if length > 30)
            run_on_penalty = run_on_sentences / len(sentences)
            
            # Check for too many short sentences (< 5 words)
            short_sentences = sum(1 for length in sentence_lengths if length < 5)
            short_penalty = short_sentences / len(sentences)
            
            structure_score = (length_score + variation_score) / 2
            structure_score -= (run_on_penalty + short_penalty) / 2
            
            return max(0, min(1, structure_score))
            
        except Exception as e:
            logger.error(f"Sentence structure analysis error: {e}")
            return 0.5
    
    async def _assess_originality(self, text: str) -> float:
        """Assess content originality using AI detection"""        
        try:
            # Use LLM to assess originality
            originality_prompt = f"""            Analyze the following text for originality and uniqueness. Rate from 0-1 where:
            0 = Generic/clichéd content
            0.5 = Some original elements mixed with common phrases
            1 = Highly original and unique content
            
            Text: "{text[:500]}..."
            
            Provide only a numerical score between 0 and 1.
            """            
            response = await self.llm_engine.generate_response(
                prompt=originality_prompt,
                max_tokens=10,
                temperature=0.1
            )
            
            # Extract numerical score
            try:
                score = float(response.strip())
                return max(0, min(1, score))
            except ValueError:
                return 0.5  # Default if parsing fails
                
        except Exception as e:
            logger.error(f"Originality assessment error: {e}")
            return 0.5
    
    def _assess_tone_consistency(self, text: str) -> float:
        """Assess tone consistency throughout the text"""        
        try:
            # Split text into chunks for analysis
            sentences = sent_tokenize(text)
            if len(sentences) < 2:
                return 1.0  # Single sentence is consistent by definition
            
            chunk_size = max(2, len(sentences) // 5)  # Analyze in chunks
            chunks = [
                ' '.join(sentences[i:i+chunk_size]) 
                for i in range(0, len(sentences), chunk_size)
            ]
            
            # Analyze sentiment of each chunk
            chunk_sentiments = []
            for chunk in chunks:
                sentiment = self.sentiment_analyzer.polarity_scores(chunk)
                chunk_sentiments.append(sentiment['compound'])
            
            # Calculate consistency (low variance = high consistency)
            if len(chunk_sentiments) > 1:
                sentiment_std = np.std(chunk_sentiments)
                consistency_score = 1 - min(1, sentiment_std)  # Normalize
            else:
                consistency_score = 1.0
            
            return consistency_score
            
        except Exception as e:
            logger.error(f"Tone consistency assessment error: {e}")
            return 0.5
    
    def _assess_engagement_potential(self, text: str) -> float:
        """Assess content engagement potential"""        
        try:
            # Engagement indicators
            engagement_words = [
                'you', 'your', 'we', 'our', 'discover', 'learn', 'amazing',
                'incredible', 'must-have', 'essential', 'revolutionary'
            ]
            
            question_marks = text.count('?')
            exclamation_marks = text.count('!')
            words = word_tokenize(text.lower())
            
            # Calculate engagement metrics
            engagement_word_ratio = sum(1 for word in words if word in engagement_words) / max(len(words), 1)
            punctuation_ratio = (question_marks + exclamation_marks) / max(len(text), 1)
            
            # Check for call-to-action phrases
            cta_phrases = ['click here', 'learn more', 'get started', 'join now', 'try today']
            has_cta = any(phrase in text.lower() for phrase in cta_phrases)
            
            # Calculate engagement score
            engagement_score = (
                engagement_word_ratio * 0.4 +
                punctuation_ratio * 100 * 0.3 +
                (0.3 if has_cta else 0.1) * 0.3
            )
            
            return max(0, min(1, engagement_score))
            
        except Exception as e:
            logger.error(f"Engagement assessment error: {e}")
            return 0.5
    
    def _assess_seo_quality(self, text: str, seo_requirements: Dict[str, Any]) -> float:
        """Assess SEO quality of text content"""        
        try:
            seo_score = 0.0
            total_checks = 0
            
            # Keyword density check
            target_keywords = seo_requirements.get('keywords', [])
            if target_keywords:
                words = word_tokenize(text.lower())
                for keyword in target_keywords:
                    keyword_count = text.lower().count(keyword.lower())
                    keyword_density = keyword_count / max(len(words), 1)
                    
                    # Optimal density is 1-3%
                    if 0.01 <= keyword_density <= 0.03:
                        seo_score += 1
                    elif keyword_density > 0:
                        seo_score += 0.5  # Present but not optimal
                    
                    total_checks += 1
            
            # Content length check
            word_count = len(word_tokenize(text))
            min_words = seo_requirements.get('min_words', 300)
            if word_count >= min_words:
                seo_score += 1
            else:
                seo_score += word_count / min_words
            total_checks += 1
            
            # Readability for SEO
            readability = flesch_reading_ease(text)
            if readability >= 60:  # Good readability for SEO
                seo_score += 1
            else:
                seo_score += readability / 60
            total_checks += 1
            
            return seo_score / max(total_checks, 1)
            
        except Exception as e:
            logger.error(f"SEO assessment error: {e}")
            return 0.5
    
    async def _assess_brand_alignment(
        self,
        text: str,
        brand_guidelines: Dict[str, Any]
    ) -> float:
        """Assess brand alignment using guidelines"""        
        try:
            alignment_score = 0.0
            total_checks = 0
            
            # Tone alignment
            required_tone = brand_guidelines.get('tone')
            if required_tone:
                sentiment = self.sentiment_analyzer.polarity_scores(text)
                
                tone_mapping = {
                    'positive': sentiment['pos'],
                    'negative': sentiment['neg'],
                    'neutral': sentiment['neu'],
                    'professional': 1 - abs(sentiment['compound'])
                }
                
                tone_score = tone_mapping.get(required_tone.lower(), 0.5)
                alignment_score += tone_score
                total_checks += 1
            
            # Vocabulary alignment
            preferred_terms = brand_guidelines.get('preferred_terms', [])
            avoided_terms = brand_guidelines.get('avoided_terms', [])
            
            if preferred_terms:
                used_preferred = sum(1 for term in preferred_terms if term.lower() in text.lower())
                preference_score = used_preferred / len(preferred_terms)
                alignment_score += preference_score
                total_checks += 1
            
            if avoided_terms:
                used_avoided = sum(1 for term in avoided_terms if term.lower() in text.lower())
                avoidance_score = 1 - (used_avoided / max(len(avoided_terms), 1))
                alignment_score += avoidance_score
                total_checks += 1
            
            return alignment_score / max(total_checks, 1)
            
        except Exception as e:
            logger.error(f"Brand alignment assessment error: {e}")
            return 0.5
    
    async def _assess_image_quality(
        self,
        content: Dict[str, Any],
        criteria: QualityCriteria
    ) -> QualityMetrics:
        """Assess image content quality"""        
        metrics = QualityMetrics()
        
        try:
            # Load image
            image_path = content.get('image_path') or content.get('file_path')
            if not image_path:
                metrics.issues_found.append({
                    "type": "error",
                    "message": "No image path provided"
                })
                return metrics
            
            # Basic image analysis
            image = Image.open(image_path)
            
            # Resolution analysis
            width, height = image.size
            total_pixels = width * height
            
            # Quality thresholds
            min_pixels = criteria.content_requirements.get('min_resolution', 1000000)  # 1MP default
            recommended_pixels = criteria.content_requirements.get('recommended_resolution', 4000000)  # 4MP
            
            if total_pixels >= recommended_pixels:
                resolution_score = 1.0
            elif total_pixels >= min_pixels:
                resolution_score = 0.7
            else:
                resolution_score = total_pixels / min_pixels
                metrics.quality_warnings.append("Image resolution below recommended minimum")
            
            # Image sharpness analysis
            image_array = np.array(image.convert('L'))  # Convert to grayscale
            laplacian_var = cv2.Laplacian(image_array, cv2.CV_64F).var()
            sharpness_score = min(1.0, laplacian_var / 1000)  # Normalize
            
            if sharpness_score < 0.3:
                metrics.quality_warnings.append("Image appears blurry or lacks sharpness")
            
            # Color analysis
            if image.mode == 'RGB':
                stat = ImageStat.Stat(image)
                color_variance = np.var(stat.mean)
                color_score = min(1.0, color_variance / 10000)  # Normalize
            else:
                color_score = 0.5
            
            # Aspect ratio analysis
            aspect_ratio = width / height
            standard_ratios = [16/9, 4/3, 1/1, 3/2, 2/3]  # Common ratios
            closest_ratio = min(standard_ratios, key=lambda r: abs(r - aspect_ratio))
            ratio_difference = abs(aspect_ratio - closest_ratio)
            aspect_score = max(0, 1 - ratio_difference)
            
            # Set technical quality score
            metrics.technical_quality_score = (
                resolution_score * 0.4 +
                sharpness_score * 0.3 +
                color_score * 0.2 +
                aspect_score * 0.1
            )
            
            # Overall score for images is primarily technical quality
            metrics.overall_score = metrics.technical_quality_score
            
            # Add image-specific suggestions
            if sharpness_score < 0.5:
                metrics.suggestions.append("Consider using a sharper image or applying sharpening filters")
            
            if resolution_score < 0.7:
                metrics.suggestions.append("Use higher resolution images for better quality")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Image quality assessment error: {e}")
            metrics.issues_found.append({
                "type": "error",
                "message": f"Image analysis failed: {str(e)}"
            })
            return metrics
    
    async def _assess_audio_quality(
        self,
        content: Dict[str, Any],
        criteria: QualityCriteria
    ) -> QualityMetrics:
        """Assess audio content quality"""        
        metrics = QualityMetrics()
        
        try:
            # Load audio
            audio_path = content.get('audio_path') or content.get('file_path')
            if not audio_path:
                metrics.issues_found.append({
                    "type": "error",
                    "message": "No audio path provided"
                })
                return metrics
            
            # Load audio with librosa
            y, sr = librosa.load(audio_path)
            duration = len(y) / sr
            
            # Audio quality analysis
            
            # 1. Signal-to-noise ratio
            # Simple SNR estimation
            signal_power = np.mean(y ** 2)
            noise_power = np.mean((y - scipy.signal.medfilt(y, kernel_size=3)) ** 2)
            snr = 10 * np.log10(signal_power / max(noise_power, 1e-10))
            snr_score = min(1.0, max(0, (snr - 10) / 30))  # Normalize 10-40 dB to 0-1
            
            # 2. Dynamic range
            dynamic_range = np.max(y) - np.min(y)
            dynamic_score = min(1.0, dynamic_range / 2)  # Normalize assuming max range of 2
            
            # 3. Clipping detection
            clipping_threshold = 0.95
            clipped_samples = np.sum(np.abs(y) > clipping_threshold)
            clipping_ratio = clipped_samples / len(y)
            clipping_score = max(0, 1 - clipping_ratio * 100)
            
            if clipping_ratio > 0.01:  # More than 1% clipped
                metrics.quality_warnings.append("Audio has significant clipping distortion")
            
            # 4. Frequency response analysis
            freqs = np.fft.fftfreq(len(y), 1/sr)
            fft = np.fft.fft(y)
            magnitude = np.abs(fft)
            
            # Check for frequency balance
            low_freq_power = np.sum(magnitude[np.abs(freqs) < 500])
            mid_freq_power = np.sum(magnitude[(np.abs(freqs) >= 500) & (np.abs(freqs) < 4000)])
            high_freq_power = np.sum(magnitude[np.abs(freqs) >= 4000])
            
            total_power = low_freq_power + mid_freq_power + high_freq_power
            if total_power > 0:
                freq_balance_score = 1 - np.std([
                    low_freq_power / total_power,
                    mid_freq_power / total_power,
                    high_freq_power / total_power
                ])
            else:
                freq_balance_score = 0
            
            # 5. Duration check
            min_duration = criteria.content_requirements.get('min_duration', 5)  # 5 seconds
            max_duration = criteria.content_requirements.get('max_duration', 300)  # 5 minutes
            
            if min_duration <= duration <= max_duration:
                duration_score = 1.0
            elif duration < min_duration:
                duration_score = duration / min_duration
                metrics.quality_warnings.append(f"Audio duration ({duration:.1f}s) is below minimum ({min_duration}s)")
            else:
                duration_score = max_duration / duration
                metrics.quality_warnings.append(f"Audio duration ({duration:.1f}s) exceeds maximum ({max_duration}s)")
            
            # Calculate technical quality score
            metrics.technical_quality_score = (
                snr_score * 0.3 +
                dynamic_score * 0.2 +
                clipping_score * 0.25 +
                freq_balance_score * 0.15 +
                duration_score * 0.1
            )
            
            # Overall score for audio is primarily technical quality
            metrics.overall_score = metrics.technical_quality_score
            
            # Add audio-specific suggestions
            if snr_score < 0.5:
                metrics.suggestions.append("Consider noise reduction to improve audio quality")
            
            if clipping_score < 0.8:
                metrics.suggestions.append("Reduce input gain to prevent clipping distortion")
            
            if freq_balance_score < 0.6:
                metrics.suggestions.append("Apply EQ to balance frequency response")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Audio quality assessment error: {e}")
            metrics.issues_found.append({
                "type": "error",
                "message": f"Audio analysis failed: {str(e)}"
            })
            return metrics
    
    async def _assess_video_quality(
        self,
        content: Dict[str, Any],
        criteria: QualityCriteria
    ) -> QualityMetrics:
        """Assess video content quality"""        
        metrics = QualityMetrics()
        
        try:
            video_path = content.get('video_path') or content.get('file_path')
            if not video_path:
                metrics.issues_found.append({
                    "type": "error",
                    "message": "No video path provided"
                })
                return metrics
            
            # Load video with OpenCV
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                metrics.issues_found.append({
                    "type": "error",
                    "message": "Cannot open video file"
                })
                return metrics
            
            # Video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Resolution analysis
            total_pixels = width * height
            min_pixels = criteria.content_requirements.get('min_resolution', 1920*1080)  # HD default
            recommended_pixels = criteria.content_requirements.get('recommended_resolution', 3840*2160)  # 4K
            
            if total_pixels >= recommended_pixels:
                resolution_score = 1.0
            elif total_pixels >= min_pixels:
                resolution_score = 0.7
            else:
                resolution_score = total_pixels / min_pixels
                metrics.quality_warnings.append("Video resolution below recommended minimum")
            
            # Frame rate analysis
            min_fps = criteria.content_requirements.get('min_fps', 24)
            recommended_fps = criteria.content_requirements.get('recommended_fps', 30)
            
            if fps >= recommended_fps:
                fps_score = 1.0
            elif fps >= min_fps:
                fps_score = 0.7
            else:
                fps_score = fps / min_fps
                metrics.quality_warnings.append(f"Frame rate ({fps:.1f}) below minimum ({min_fps})")
            
            # Sample frames for quality analysis
            sample_frames = []
            frame_step = max(1, int(frame_count / 10))  # Sample 10 frames
            
            for i in range(0, int(frame_count), frame_step):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    sample_frames.append(frame)
                if len(sample_frames) >= 10:
                    break
            
            cap.release()
            
            # Analyze sample frames
            if sample_frames:
                # Sharpness analysis
                sharpness_scores = []
                for frame in sample_frames:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                    sharpness_scores.append(laplacian_var)
                
                avg_sharpness = np.mean(sharpness_scores)
                sharpness_score = min(1.0, avg_sharpness / 1000)  # Normalize
                
                # Brightness analysis
                brightness_scores = []
                for frame in sample_frames:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    brightness = np.mean(gray)
                    brightness_scores.append(brightness)
                
                avg_brightness = np.mean(brightness_scores)
                # Optimal brightness is around 127 (middle gray)
                brightness_score = 1 - abs(avg_brightness - 127) / 127
                
            else:
                sharpness_score = 0.5
                brightness_score = 0.5
                metrics.issues_found.append({
                    "type": "warning",
                    "message": "Could not sample video frames for analysis"
                })
            
            # Duration check
            min_duration = criteria.content_requirements.get('min_duration', 10)  # 10 seconds
            max_duration = criteria.content_requirements.get('max_duration', 600)  # 10 minutes
            
            if min_duration <= duration <= max_duration:
                duration_score = 1.0
            elif duration < min_duration:
                duration_score = duration / min_duration
                metrics.quality_warnings.append(f"Video duration ({duration:.1f}s) below minimum ({min_duration}s)")
            else:
                duration_score = max_duration / duration
                metrics.quality_warnings.append(f"Video duration ({duration:.1f}s) exceeds maximum ({max_duration}s)")
            
            # Calculate technical quality score
            metrics.technical_quality_score = (
                resolution_score * 0.3 +
                fps_score * 0.2 +
                sharpness_score * 0.25 +
                brightness_score * 0.15 +
                duration_score * 0.1
            )
            
            # Overall score for video is primarily technical quality
            metrics.overall_score = metrics.technical_quality_score
            
            # Add video-specific suggestions
            if resolution_score < 0.7:
                metrics.suggestions.append("Consider using higher resolution for better quality")
            
            if fps_score < 0.7:
                metrics.suggestions.append("Increase frame rate for smoother playback")
            
            if sharpness_score < 0.5:
                metrics.suggestions.append("Improve focus or apply sharpening filters")
            
            if brightness_score < 0.6:
                metrics.suggestions.append("Adjust brightness levels for optimal viewing")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Video quality assessment error: {e}")
            metrics.issues_found.append({
                "type": "error",
                "message": f"Video analysis failed: {str(e)}"
            })
            return metrics
    
    async def _assess_document_quality(
        self,
        content: Dict[str, Any],
        criteria: QualityCriteria
    ) -> QualityMetrics:
        """Assess document content quality"""        
        # For documents, extract text and perform text quality assessment
        text_content = content.get("extracted_text", "")
        if text_content:
            content_with_text = {**content, "text": text_content}
            return await self._assess_text_quality(content_with_text, criteria)
        else:
            metrics = QualityMetrics()
            metrics.issues_found.append({
                "type": "error",
                "message": "No text extracted from document for quality analysis"
            })
            return metrics
    
    async def _assess_multimedia_quality(
        self,
        content: Dict[str, Any],
        criteria: QualityCriteria
    ) -> QualityMetrics:
        """Assess multimedia content quality (combination of formats)"""        
        metrics = QualityMetrics()
        
        try:
            # Assess each component separately and combine scores
            component_scores = []
            
            if "text" in content or "body" in content:
                text_metrics = await self._assess_text_quality(content, criteria)
                component_scores.append(text_metrics.overall_score)
                metrics.issues_found.extend(text_metrics.issues_found)
                metrics.suggestions.extend(text_metrics.suggestions)
            
            if "image_path" in content or "image_data" in content:
                image_metrics = await self._assess_image_quality(content, criteria)
                component_scores.append(image_metrics.overall_score)
                metrics.issues_found.extend(image_metrics.issues_found)
                metrics.suggestions.extend(image_metrics.suggestions)
            
            if "audio_path" in content or "audio_data" in content:
                audio_metrics = await self._assess_audio_quality(content, criteria)
                component_scores.append(audio_metrics.overall_score)
                metrics.issues_found.extend(audio_metrics.issues_found)
                metrics.suggestions.extend(audio_metrics.suggestions)
            
            if "video_path" in content or "video_data" in content:
                video_metrics = await self._assess_video_quality(content, criteria)
                component_scores.append(video_metrics.overall_score)
                metrics.issues_found.extend(video_metrics.issues_found)
                metrics.suggestions.extend(video_metrics.suggestions)
            
            # Calculate overall score as weighted average
            if component_scores:
                metrics.overall_score = np.mean(component_scores)
            else:
                metrics.overall_score = 0.0
                metrics.issues_found.append({
                    "type": "error",
                    "message": "No recognizable content components found for analysis"
                })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Multimedia quality assessment error: {e}")
            metrics.issues_found.append({
                "type": "error",
                "message": f"Multimedia analysis failed: {str(e)}"
            })
            return metrics
    
    def _calculate_overall_score(self, metrics: QualityMetrics) -> float:
        """Calculate overall quality score from individual metrics"""        
        try:
            # Weight different quality aspects
            score_components = []
            
            if metrics.grammar_score > 0:
                score_components.append(("grammar", metrics.grammar_score, 0.2))
            
            if metrics.spelling_score > 0:
                score_components.append(("spelling", metrics.spelling_score, 0.15))
            
            if metrics.readability_score > 0:
                score_components.append(("readability", metrics.readability_score / 100, 0.15))
            
            if metrics.originality_score > 0:
                score_components.append(("originality", metrics.originality_score, 0.15))
            
            if metrics.sentence_structure_score > 0:
                score_components.append(("structure", metrics.sentence_structure_score, 0.1))
            
            if metrics.tone_consistency_score > 0:
                score_components.append(("tone", metrics.tone_consistency_score, 0.1))
            
            if metrics.engagement_potential_score > 0:
                score_components.append(("engagement", metrics.engagement_potential_score, 0.1))
            
            if metrics.technical_quality_score > 0:
                score_components.append(("technical", metrics.technical_quality_score, 0.3))
            
            # Calculate weighted average
            if score_components:
                total_weight = sum(weight for _, _, weight in score_components)
                weighted_sum = sum(score * weight for _, score, weight in score_components)
                overall_score = weighted_sum / total_weight
            else:
                overall_score = 0.0
            
            return max(0, min(1, overall_score))
            
        except Exception as e:
            logger.error(f"Overall score calculation error: {e}")
            return 0.5
    
    def _generate_quality_warnings(
        self,
        metrics: QualityMetrics,
        criteria: QualityCriteria
    ) -> List[str]:
        """Generate quality warnings based on metrics and criteria"""        
        warnings = []
        
        try:
            # Get quality thresholds for target level
            thresholds = self.quality_thresholds.get(
                criteria.target_quality_level.value,
                self.quality_thresholds[QualityLevel.PROFESSIONAL.value]
            )
            
            # Check individual metrics against thresholds
            if metrics.grammar_score < thresholds.get("grammar_score", 0.8):
                warnings.append("Grammar quality below target level")
            
            if metrics.spelling_score < 0.95:  # High standard for spelling
                warnings.append("Spelling errors detected")
            
            if metrics.readability_score < thresholds.get("readability_score", 60):
                warnings.append("Readability below target level")
            
            if metrics.originality_score < thresholds.get("originality_score", 0.7):
                warnings.append("Content originality below target level")
            
            if metrics.overall_score < thresholds.get("overall_score", 0.75):
                warnings.append("Overall quality below target level")
            
            # Check for critical issues
            critical_issues = [issue for issue in metrics.issues_found if issue.get("type") == "error"]
            if critical_issues:
                warnings.append(f"Found {len(critical_issues)} critical issues requiring attention")
            
            return warnings
            
        except Exception as e:
            logger.error(f"Warning generation error: {e}")
            return ["Unable to generate quality warnings"]
    
    async def _generate_validation_result(
        self,
        metrics: QualityMetrics,
        criteria: QualityCriteria,
        validation_id: str
    ) -> Dict[str, Any]:
        """Generate comprehensive validation result"""        
        try:
            passed_checks = []
            failed_checks = []
            
            # Get thresholds for target quality level
            thresholds = self.quality_thresholds.get(
                criteria.target_quality_level.value,
                self.quality_thresholds[QualityLevel.PROFESSIONAL.value]
            )
            
            # Check each dimension
            for dimension in criteria.required_dimensions:
                dimension_score = metrics.dimension_scores.get(dimension.value, 0)
                min_score = criteria.minimum_scores.get(dimension.value, thresholds.get(dimension.value, 0.7))
                
                if dimension_score >= min_score:
                    passed_checks.append(f"{dimension.value}: {dimension_score:.2f} (≥ {min_score})")
                else:
                    failed_checks.append(f"{dimension.value}: {dimension_score:.2f} (< {min_score})")
            
            # Overall quality check
            min_overall = criteria.minimum_scores.get("overall", thresholds.get("overall_score", 0.75))
            if metrics.overall_score >= min_overall:
                passed_checks.append(f"Overall quality: {metrics.overall_score:.2f} (≥ {min_overall})")
            else:
                failed_checks.append(f"Overall quality: {metrics.overall_score:.2f} (< {min_overall})")
            
            # Determine next steps
            next_steps = []
            if failed_checks:
                next_steps.append("Address failed quality checks")
                next_steps.append("Review and implement suggested improvements")
                if metrics.overall_score < 0.5:
                    next_steps.append("Consider significant content revision")
                else:
                    next_steps.append("Make targeted improvements to specific areas")
            else:
                next_steps.append("Content meets quality standards")
                if metrics.overall_score < 0.9:
                    next_steps.append("Consider optional improvements for excellence")
                next_steps.append("Content ready for publication")
            
            return {
                "validation_id": validation_id,
                "passed_checks": passed_checks,
                "failed_checks": failed_checks,
                "next_steps": next_steps,
                "quality_met": len(failed_checks) == 0,
                "improvement_areas": len(failed_checks)
            }
            
        except Exception as e:
            logger.error(f"Validation result generation error: {e}")
            return {
                "validation_id": validation_id,
                "passed_checks": [],
                "failed_checks": ["Validation process encountered errors"],
                "next_steps": ["Review content and rerun quality check"],
                "quality_met": False,
                "improvement_areas": 1
            }
    
    def _determine_quality_level(self, metrics: QualityMetrics) -> str:
        """Determine quality level based on metrics"""        
        score = metrics.overall_score
        
        if score >= 0.9:
            return QualityLevel.ENTERPRISE.value
        elif score >= 0.85:
            return QualityLevel.PREMIUM.value
        elif score >= 0.75:
            return QualityLevel.PROFESSIONAL.value
        elif score >= 0.6:
            return QualityLevel.REVIEW_READY.value
        else:
            return QualityLevel.DRAFT.value
    
    def _serialize_quality_metrics(self, metrics: QualityMetrics) -> Dict[str, Any]:
        """Serialize quality metrics for API response"""        
        return {
            "overall_score": round(metrics.overall_score, 3),
            "dimension_scores": {k: round(v, 3) for k, v in metrics.dimension_scores.items()},
            "readability_score": round(metrics.readability_score, 2),
            "grammar_score": round(metrics.grammar_score, 3),
            "spelling_score": round(metrics.spelling_score, 3),
            "vocabulary_richness": round(metrics.vocabulary_richness, 3),
            "originality_score": round(metrics.originality_score, 3),
            "tone_consistency_score": round(metrics.tone_consistency_score, 3),
            "engagement_potential_score": round(metrics.engagement_potential_score, 3),
            "technical_quality_score": round(metrics.technical_quality_score, 3),
            "seo_score": round(metrics.seo_score, 3),
            "brand_alignment_score": round(metrics.brand_alignment_score, 3),
            "issues_count": len(metrics.issues_found),
            "suggestions_count": len(metrics.suggestions),
            "warnings_count": len(metrics.quality_warnings)
        }
    
    async def _generate_quality_recommendations(
        self,
        metrics: QualityMetrics,
        criteria: QualityCriteria
    ) -> List[str]:
        """Generate actionable quality improvement recommendations"""        
        recommendations = []
        
        try:
            # Grammar and spelling recommendations
            if metrics.grammar_score < 0.8:
                recommendations.append("Review and correct grammar errors using suggested fixes")
            
            if metrics.spelling_score < 0.95:
                recommendations.append("Correct spelling errors and verify proper terminology")
            
            # Readability recommendations
            if metrics.readability_score < 50:
                recommendations.append("Simplify language and sentence structure for better readability")
            elif metrics.readability_score > 80:
                recommendations.append("Consider adding more sophisticated vocabulary for professional appeal")
            
            # Structure recommendations
            if metrics.sentence_structure_score < 0.6:
                recommendations.append("Vary sentence lengths and improve sentence structure")
            
            # Engagement recommendations
            if metrics.engagement_potential_score < 0.5:
                recommendations.append("Add more engaging elements like questions, examples, or call-to-actions")
            
            # Originality recommendations
            if metrics.originality_score < 0.6:
                recommendations.append("Increase content originality with unique insights and perspectives")
            
            # Technical quality recommendations (for media content)
            if metrics.technical_quality_score > 0 and metrics.technical_quality_score < 0.7:
                recommendations.append("Improve technical quality aspects like resolution, clarity, or audio quality")
            
            # SEO recommendations
            if metrics.seo_score > 0 and metrics.seo_score < 0.7:
                recommendations.append("Optimize content for SEO with better keyword usage and structure")
            
            # Brand alignment recommendations
            if metrics.brand_alignment_score > 0 and metrics.brand_alignment_score < 0.7:
                recommendations.append("Better align content with brand voice and guidelines")
            
            # Issue-specific recommendations
            error_count = len([issue for issue in metrics.issues_found if issue.get("type") == "error"])
            if error_count > 0:
                recommendations.append(f"Address {error_count} critical issues identified in detailed analysis")
            
            # Add existing suggestions from metrics
            recommendations.extend(metrics.suggestions[:3])  # Add top 3 suggestions
            
            return recommendations[:7]  # Limit to top 7 recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation error: {e}")
            return ["Review content for quality improvements"]
    
    async def _store_quality_assessment(
        self,
        validation_id: str,
        user_id: str,
        content: Dict[str, Any],
        metrics: QualityMetrics,
        db: AsyncSession
    ):
        """Store quality assessment record in database"""        
        try:
            assessment_record = {
                "id": validation_id,
                "user_id": user_id,
                "content_type": self._determine_content_format(content).value,
                "overall_score": metrics.overall_score,
                "dimension_scores": metrics.dimension_scores,
                "detailed_metrics": self._serialize_quality_metrics(metrics),
                "issues_found": len(metrics.issues_found),
                "suggestions_count": len(metrics.suggestions),
                "quality_level": self._determine_quality_level(metrics),
                "assessment_data": {
                    "issues": metrics.issues_found,
                    "suggestions": metrics.suggestions,
                    "warnings": metrics.quality_warnings
                },
                "created_at": datetime.now(timezone.utc)
            }
            
            # Store in cache for quick access
            cache_key = f"quality_assessment:{validation_id}"
            await self.cache_manager.set(cache_key, assessment_record, ttl=3600)
            
            logger.info(f"Quality assessment stored: {validation_id}")
            
        except Exception as e:
            logger.error(f"Error storing quality assessment: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for quality controller"""        return {
            "status": "healthy",
            "grammar_tool_available": self.grammar_tool is not None,
            "ai_models_loaded": bool(self.quality_classifier and self.toxicity_detector),
            "quality_levels_supported": len(self.quality_thresholds),
            "cache_status": "active" if self.cache_manager else "inactive",
            "last_check": datetime.now(timezone.utc).isoformat()
        }


class ContentValidator:
    """Advanced content validation and compliance checker"""    
    def __init__(self):
        self.quality_controller = QualityController()
        self.performance_monitor = PerformanceMonitor("content_validator")
    
    async def validate_batch_content(
        self,
        content_batch: List[Dict[str, Any]],
        validation_criteria: Dict[str, Any],
        user_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Validate multiple content pieces in batch"""        
        async with self.performance_monitor.track_operation("batch_validation"):
            try:
                batch_results = []
                
                # Process each content item
                for i, content_item in enumerate(content_batch):
                    try:
                        result = await self.quality_controller.validate_content(
                            content=content_item,
                            criteria=validation_criteria,
                            user_id=user_id,
                            db=db
                        )
                        
                        batch_results.append({
                            "index": i,
                            "content_id": content_item.get("id", f"item_{i}"),
                            "validation_result": result,
                            "status": "completed"
                        })
                        
                    except Exception as e:
                        batch_results.append({
                            "index": i,
                            "content_id": content_item.get("id", f"item_{i}"),
                            "error": str(e),
                            "status": "failed"
                        })
                
                # Calculate batch statistics
                successful_validations = [r for r in batch_results if r["status"] == "completed"]
                failed_validations = [r for r in batch_results if r["status"] == "failed"]
                
                if successful_validations:
                    avg_score = np.mean([
                        r["validation_result"]["overall_score"] 
                        for r in successful_validations
                    ])
                    quality_distribution = Counter([
                        r["validation_result"].get("quality_level", "unknown")
                        for r in successful_validations
                    ])
                else:
                    avg_score = 0.0
                    quality_distribution = {}
                
                return {
                    "batch_id": str(uuid.uuid4()),
                    "total_items": len(content_batch),
                    "successful_validations": len(successful_validations),
                    "failed_validations": len(failed_validations),
                    "average_quality_score": round(avg_score, 3),
                    "quality_distribution": dict(quality_distribution),
                    "validation_results": batch_results,
                    "processed_at": datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                logger.error(f"Batch validation error: {e}")
                raise HTTPException(status_code=500, detail=f"Batch validation failed: {str(e)}")
