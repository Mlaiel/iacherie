"""Translation Quality Assessment - Advanced Quality Validation System
================================================================================
Module: backend/languages/translation_quality.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Translation Quality Engine - BLEU, METEOR, BERT-Score Evaluation
Responsibility: Translation quality assessment, validation, human feedback integration
Technologies: Python, BLEU, METEOR, BERT-Score, Quality Metrics, Human Feedback
================================================================================

⚠️  PROPRIETARY SOFTWARE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Translation input → Quality metric calculation → Human feedback integration → 
Error pattern analysis → Quality improvement recommendations → Final scoring
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import json
import statistics
import re
from pathlib import Path

try:
    import nltk
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    from nltk.translate.meteor_score import meteor_score
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    from bert_score import score as bert_score
    BERT_SCORE_AVAILABLE = True
except ImportError:
    BERT_SCORE_AVAILABLE = False

logger = logging.getLogger(__name__)


class QualityMetric(Enum):
    """Quality assessment metrics"""
    BLEU = "bleu"
    METEOR = "meteor"
    BERT_SCORE = "bert_score"
    HUMAN_EVALUATION = "human_evaluation"
    FLUENCY = "fluency"
    ADEQUACY = "adequacy"
    CONSISTENCY = "consistency"
    TERMINOLOGY = "terminology"


class QualityLevel(Enum):
    """Overall quality levels"""
    EXCELLENT = "excellent"  # 95-100%
    VERY_GOOD = "very_good"  # 90-94%
    GOOD = "good"           # 80-89%
    FAIR = "fair"           # 70-79%
    POOR = "poor"           # 60-69%
    UNACCEPTABLE = "unacceptable"  # < 60%


class ErrorType(Enum):
    """Types of translation errors"""
    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"
    FLUENCY = "fluency"
    ACCURACY = "accuracy"
    TERMINOLOGY = "terminology"
    CULTURAL = "cultural"
    FORMATTING = "formatting"
    COMPLETENESS = "completeness"


class ImprovementArea(Enum):
    """Areas for translation improvement"""
    CONTEXT_UNDERSTANDING = "context_understanding"
    DOMAIN_KNOWLEDGE = "domain_knowledge"
    CULTURAL_ADAPTATION = "cultural_adaptation"
    FLUENCY_ENHANCEMENT = "fluency_enhancement"
    TERMINOLOGY_CONSISTENCY = "terminology_consistency"
    GRAMMAR_ACCURACY = "grammar_accuracy"


@dataclass
class QualityRequest:
    """Request for quality assessment"""
    original_text: str
    translated_text: str
    reference_translation: Optional[str] = None
    source_language: str = "auto"
    target_language: str = "auto"
    domain: Optional[str] = None
    context: Optional[str] = None
    human_feedback: Optional[Dict[str, Any]] = None
    metrics_to_compute: List[QualityMetric] = field(default_factory=lambda: [
        QualityMetric.BLEU, QualityMetric.BERT_SCORE, QualityMetric.FLUENCY
    ])


@dataclass
class ErrorAnalysis:
    """Analysis of translation errors"""
    error_type: ErrorType
    severity: float  # 0.0-1.0
    location: str
    description: str
    suggestion: Optional[str] = None


@dataclass
class QualityResult:
    """Comprehensive quality assessment result"""
    overall_score: float
    quality_level: QualityLevel
    metric_scores: Dict[QualityMetric, float] = field(default_factory=dict)
    error_analysis: List[ErrorAnalysis] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    improvement_areas: List[ImprovementArea] = field(default_factory=list)
    confidence: float = 0.0
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HumanFeedback:
    """Human feedback for translation quality"""
    overall_rating: float  # 1-5 scale
    fluency_rating: float
    adequacy_rating: float
    comments: str
    specific_errors: List[ErrorAnalysis] = field(default_factory=list)
    evaluator_id: Optional[str] = None
    evaluation_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class QualityImprovement:
    """Quality improvement recommendations"""
    area: ImprovementArea
    priority: float  # 0.0-1.0
    description: str
    suggested_actions: List[str]
    estimated_impact: float  # Expected quality improvement


class TranslationQualityEngine:
    """
    Advanced translation quality assessment engine supporting multiple
    quality metrics and human feedback integration
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize quality assessment engine"""
        self.config = config or {}
        self.quality_cache = {}
        self.feedback_database = {}
        self.error_patterns = {}
        
        # Quality thresholds
        self.quality_thresholds = {
            QualityLevel.EXCELLENT: 0.95,
            QualityLevel.VERY_GOOD: 0.90,
            QualityLevel.GOOD: 0.80,
            QualityLevel.FAIR: 0.70,
            QualityLevel.POOR: 0.60
        }
        
        # Metric weights for overall score calculation
        self.metric_weights = {
            QualityMetric.BLEU: 0.25,
            QualityMetric.METEOR: 0.20,
            QualityMetric.BERT_SCORE: 0.30,
            QualityMetric.FLUENCY: 0.15,
            QualityMetric.HUMAN_EVALUATION: 0.10
        }
        
        # Initialize NLTK data if available
        if NLTK_AVAILABLE:
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('wordnet', quiet=True)
                nltk.download('omw-1.4', quiet=True)
            except:
                pass
        
        logger.info("TranslationQualityEngine initialized")
    
    async def assess_quality(self, request: QualityRequest) -> QualityResult:
        """
        Perform comprehensive quality assessment
        
        Args:
            request: Quality assessment request
            
        Returns:
            QualityResult with scores, analysis, and recommendations
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            result = QualityResult(
                overall_score=0.0,
                quality_level=QualityLevel.UNACCEPTABLE
            )
            
            # Calculate individual metrics
            for metric in request.metrics_to_compute:
                score = await self._calculate_metric(metric, request)
                result.metric_scores[metric] = score
            
            # Calculate overall score
            result.overall_score = await self._calculate_overall_score(result.metric_scores)
            
            # Determine quality level
            result.quality_level = await self._determine_quality_level(result.overall_score)
            
            # Perform error analysis
            result.error_analysis = await self._analyze_errors(request)
            
            # Generate improvement suggestions
            result.improvement_suggestions = await self._generate_improvement_suggestions(
                request, result.error_analysis
            )
            
            # Identify improvement areas
            result.improvement_areas = await self._identify_improvement_areas(
                result.error_analysis
            )
            
            # Calculate confidence
            result.confidence = await self._calculate_confidence(result)
            
            result.processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            result.metadata = {
                "source_language": request.source_language,
                "target_language": request.target_language,
                "domain": request.domain,
                "text_length": len(request.translated_text),
                "metrics_computed": [m.value for m in request.metrics_to_compute],
                "has_reference": request.reference_translation is not None
            }
            
            logger.info(f"Quality assessment completed: {result.overall_score:.3f} "
                       f"({result.quality_level.value})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in quality assessment: {str(e)}")
            return QualityResult(
                overall_score=0.0,
                quality_level=QualityLevel.UNACCEPTABLE,
                metadata={"error": str(e)}
            )
    
    async def add_human_feedback(self, translated_text: str, 
                               feedback: HumanFeedback) -> bool:
        """
        Add human feedback to improve quality assessment
        
        Args:
            translated_text: The translated text being evaluated
            feedback: Human evaluation feedback
            
        Returns:
            Success status
        """
        try:
            text_hash = self._hash_text(translated_text)
            
            if text_hash not in self.feedback_database:
                self.feedback_database[text_hash] = []
            
            self.feedback_database[text_hash].append(feedback)
            
            # Update error patterns based on feedback
            await self._update_error_patterns(feedback)
            
            logger.info(f"Human feedback added for translation (Hash: {text_hash[:8]})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding human feedback: {str(e)}")
            return False
    
    async def get_quality_recommendations(self, request: QualityRequest) -> List[QualityImprovement]:
        """
        Get detailed quality improvement recommendations
        
        Args:
            request: Quality assessment request
            
        Returns:
            List of quality improvement recommendations
        """
        quality_result = await self.assess_quality(request)
        recommendations = []
        
        # Analyze each improvement area
        for area in quality_result.improvement_areas:
            improvement = await self._generate_detailed_recommendation(
                area, request, quality_result
            )
            recommendations.append(improvement)
        
        # Sort by priority
        recommendations.sort(key=lambda x: x.priority, reverse=True)
        
        return recommendations
    
    async def _calculate_metric(self, metric: QualityMetric, 
                              request: QualityRequest) -> float:
        """Calculate specific quality metric"""
        try:
            if metric == QualityMetric.BLEU:
                return await self._calculate_bleu_score(request)
            elif metric == QualityMetric.METEOR:
                return await self._calculate_meteor_score(request)
            elif metric == QualityMetric.BERT_SCORE:
                return await self._calculate_bert_score(request)
            elif metric == QualityMetric.FLUENCY:
                return await self._calculate_fluency_score(request)
            elif metric == QualityMetric.ADEQUACY:
                return await self._calculate_adequacy_score(request)
            elif metric == QualityMetric.HUMAN_EVALUATION:
                return await self._get_human_evaluation_score(request.translated_text)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculating {metric.value}: {str(e)}")
            return 0.0
    
    async def _calculate_bleu_score(self, request: QualityRequest) -> float:
        """Calculate BLEU score"""
        if not NLTK_AVAILABLE or not request.reference_translation:
            return 0.0
        
        try:
            # Tokenize texts
            reference = request.reference_translation.split()
            candidate = request.translated_text.split()
            
            # Calculate BLEU with smoothing
            smoothie = SmoothingFunction().method4
            score = sentence_bleu([reference], candidate, smoothing_function=smoothie)
            
            return float(score)
            
        except Exception as e:
            logger.error(f"Error calculating BLEU score: {str(e)}")
            return 0.0
    
    async def _calculate_meteor_score(self, request: QualityRequest) -> float:
        """Calculate METEOR score"""
        if not NLTK_AVAILABLE or not request.reference_translation:
            return 0.0
        
        try:
            score = meteor_score([request.reference_translation], request.translated_text)
            return float(score)
            
        except Exception as e:
            logger.error(f"Error calculating METEOR score: {str(e)}")
            return 0.0
    
    async def _calculate_bert_score(self, request: QualityRequest) -> float:
        """Calculate BERT score"""
        if not BERT_SCORE_AVAILABLE or not request.reference_translation:
            return 0.0
        
        try:
            P, R, F1 = bert_score(
                [request.translated_text],
                [request.reference_translation],
                lang=request.target_language[:2] if len(request.target_language) > 2 else request.target_language
            )
            
            return float(F1.mean())
            
        except Exception as e:
            logger.error(f"Error calculating BERT score: {str(e)}")
            return 0.0
    
    async def _calculate_fluency_score(self, request: QualityRequest) -> float:
        """Calculate fluency score based on linguistic patterns"""
        text = request.translated_text
        
        # Basic fluency indicators
        indicators = {
            "sentence_structure": self._analyze_sentence_structure(text),
            "grammar_patterns": self._analyze_grammar_patterns(text),
            "word_order": self._analyze_word_order(text),
            "punctuation": self._analyze_punctuation(text)
        }
        
        # Calculate weighted fluency score
        fluency_score = (
            indicators["sentence_structure"] * 0.3 +
            indicators["grammar_patterns"] * 0.3 +
            indicators["word_order"] * 0.2 +
            indicators["punctuation"] * 0.2
        )
        
        return max(0.0, min(1.0, fluency_score))
    
    async def _calculate_adequacy_score(self, request: QualityRequest) -> float:
        """Calculate adequacy score (meaning preservation)"""
        # This is a simplified adequacy calculation
        # In production, this would use more sophisticated semantic analysis
        
        original_words = set(request.original_text.lower().split())
        translated_words = set(request.translated_text.lower().split())
        
        # Simple word overlap (not accurate for different languages)
        if len(original_words) == 0:
            return 0.0
        
        # This is a placeholder - real adequacy would require cross-lingual analysis
        overlap_ratio = len(original_words.intersection(translated_words)) / len(original_words)
        
        # Adjust for typical translation patterns
        adequacy_score = min(1.0, overlap_ratio * 2.0)
        
        return adequacy_score
    
    async def _get_human_evaluation_score(self, translated_text: str) -> float:
        """Get average human evaluation score if available"""
        text_hash = self._hash_text(translated_text)
        
        if text_hash in self.feedback_database:
            feedbacks = self.feedback_database[text_hash]
            if feedbacks:
                avg_score = statistics.mean([f.overall_rating for f in feedbacks]) / 5.0
                return avg_score
        
        return 0.0
    
    async def _calculate_overall_score(self, metric_scores: Dict[QualityMetric, float]) -> float:
        """Calculate weighted overall quality score"""
        if not metric_scores:
            return 0.0
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for metric, score in metric_scores.items():
            weight = self.metric_weights.get(metric, 0.1)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    async def _determine_quality_level(self, overall_score: float) -> QualityLevel:
        """Determine quality level from overall score"""
        for level, threshold in self.quality_thresholds.items():
            if overall_score >= threshold:
                return level
        return QualityLevel.UNACCEPTABLE
    
    async def _analyze_errors(self, request: QualityRequest) -> List[ErrorAnalysis]:
        """Analyze potential errors in translation"""
        errors = []
        text = request.translated_text
        
        # Grammar errors
        grammar_errors = self._detect_grammar_errors(text)
        errors.extend(grammar_errors)
        
        # Fluency errors
        fluency_errors = self._detect_fluency_errors(text)
        errors.extend(fluency_errors)
        
        # Formatting errors
        formatting_errors = self._detect_formatting_errors(text, request.original_text)
        errors.extend(formatting_errors)
        
        # Completeness errors
        completeness_errors = self._detect_completeness_errors(text, request.original_text)
        errors.extend(completeness_errors)
        
        return errors
    
    def _detect_grammar_errors(self, text: str) -> List[ErrorAnalysis]:
        """Detect potential grammar errors"""
        errors = []
        
        # Simple grammar checks (placeholder)
        if re.search(r'\b(a|an)\s+[aeiouAEIOU]', text):
            errors.append(ErrorAnalysis(
                error_type=ErrorType.GRAMMAR,
                severity=0.3,
                location="article usage",
                description="Potential article usage error",
                suggestion="Check indefinite article usage before vowels"
            ))
        
        return errors
    
    def _detect_fluency_errors(self, text: str) -> List[ErrorAnalysis]:
        """Detect fluency issues"""
        errors = []
        
        # Check for repeated words
        words = text.split()
        for i in range(len(words) - 1):
            if words[i].lower() == words[i + 1].lower():
                errors.append(ErrorAnalysis(
                    error_type=ErrorType.FLUENCY,
                    severity=0.4,
                    location=f"position {i}",
                    description="Repeated word detected",
                    suggestion="Remove word repetition"
                ))
        
        return errors
    
    def _detect_formatting_errors(self, translated_text: str, original_text: str) -> List[ErrorAnalysis]:
        """Detect formatting inconsistencies"""
        errors = []
        
        # Check punctuation preservation
        original_punct = re.findall(r'[.!?;:]', original_text)
        translated_punct = re.findall(r'[.!?;:]', translated_text)
        
        if len(original_punct) != len(translated_punct):
            errors.append(ErrorAnalysis(
                error_type=ErrorType.FORMATTING,
                severity=0.2,
                location="punctuation",
                description="Punctuation count mismatch",
                suggestion="Preserve punctuation from original text"
            ))
        
        return errors
    
    def _detect_completeness_errors(self, translated_text: str, original_text: str) -> List[ErrorAnalysis]:
        """Detect completeness issues"""
        errors = []
        
        # Simple length-based completeness check
        len_ratio = len(translated_text) / len(original_text) if len(original_text) > 0 else 0
        
        if len_ratio < 0.5:
            errors.append(ErrorAnalysis(
                error_type=ErrorType.COMPLETENESS,
                severity=0.8,
                location="overall",
                description="Translation appears significantly shorter than original",
                suggestion="Check if all content has been translated"
            ))
        elif len_ratio > 2.0:
            errors.append(ErrorAnalysis(
                error_type=ErrorType.COMPLETENESS,
                severity=0.4,
                location="overall",
                description="Translation appears significantly longer than original",
                suggestion="Check for unnecessary additions or repetitions"
            ))
        
        return errors
    
    def _analyze_sentence_structure(self, text: str) -> float:
        """Analyze sentence structure quality"""
        sentences = re.split(r'[.!?]+', text)
        if not sentences:
            return 0.0
        
        # Basic structure analysis
        avg_length = statistics.mean([len(s.split()) for s in sentences if s.strip()])
        
        # Optimal sentence length is typically 15-20 words
        if 10 <= avg_length <= 25:
            return 0.9
        elif 5 <= avg_length <= 35:
            return 0.7
        else:
            return 0.5
    
    def _analyze_grammar_patterns(self, text: str) -> float:
        """Analyze grammar patterns"""
        # Simplified grammar analysis
        words = text.split()
        if not words:
            return 0.0
        
        # Check for basic patterns
        has_articles = any(word.lower() in ['a', 'an', 'the'] for word in words)
        has_conjunctions = any(word.lower() in ['and', 'but', 'or', 'because'] for word in words)
        
        score = 0.5
        if has_articles:
            score += 0.2
        if has_conjunctions:
            score += 0.2
        
        return min(1.0, score)
    
    def _analyze_word_order(self, text: str) -> float:
        """Analyze word order naturalness"""
        # This is a placeholder for more sophisticated word order analysis
        # In practice, this would use language-specific models
        return 0.8
    
    def _analyze_punctuation(self, text: str) -> float:
        """Analyze punctuation usage"""
        if not text:
            return 0.0
        
        # Check for balanced punctuation
        open_brackets = text.count('(') + text.count('[') + text.count('{')
        close_brackets = text.count(')') + text.count(']') + text.count('}')
        
        if open_brackets == close_brackets:
            return 0.9
        else:
            return 0.6
    
    async def _generate_improvement_suggestions(self, request: QualityRequest, 
                                              errors: List[ErrorAnalysis]) -> List[str]:
        """Generate improvement suggestions based on error analysis"""
        suggestions = []
        
        # Group errors by type
        error_types = {}
        for error in errors:
            if error.error_type not in error_types:
                error_types[error.error_type] = []
            error_types[error.error_type].append(error)
        
        # Generate suggestions for each error type
        for error_type, error_list in error_types.items():
            if error_type == ErrorType.GRAMMAR:
                suggestions.append("Review grammar rules for the target language")
            elif error_type == ErrorType.FLUENCY:
                suggestions.append("Focus on natural word flow and sentence rhythm")
            elif error_type == ErrorType.FORMATTING:
                suggestions.append("Preserve formatting and punctuation from original text")
            elif error_type == ErrorType.COMPLETENESS:
                suggestions.append("Ensure all content is accurately translated")
        
        return suggestions
    
    async def _identify_improvement_areas(self, errors: List[ErrorAnalysis]) -> List[ImprovementArea]:
        """Identify key areas for improvement"""
        areas = set()
        
        for error in errors:
            if error.error_type == ErrorType.GRAMMAR:
                areas.add(ImprovementArea.GRAMMAR_ACCURACY)
            elif error.error_type == ErrorType.FLUENCY:
                areas.add(ImprovementArea.FLUENCY_ENHANCEMENT)
            elif error.error_type == ErrorType.CULTURAL:
                areas.add(ImprovementArea.CULTURAL_ADAPTATION)
            elif error.error_type == ErrorType.TERMINOLOGY:
                areas.add(ImprovementArea.TERMINOLOGY_CONSISTENCY)
        
        return list(areas)
    
    async def _generate_detailed_recommendation(self, area: ImprovementArea, 
                                              request: QualityRequest,
                                              quality_result: QualityResult) -> QualityImprovement:
        """Generate detailed improvement recommendation for specific area"""
        recommendations = {
            ImprovementArea.GRAMMAR_ACCURACY: QualityImprovement(
                area=area,
                priority=0.8,
                description="Improve grammatical accuracy and structure",
                suggested_actions=[
                    "Use grammar checking tools",
                    "Review target language grammar rules",
                    "Practice sentence construction patterns"
                ],
                estimated_impact=0.15
            ),
            ImprovementArea.FLUENCY_ENHANCEMENT: QualityImprovement(
                area=area,
                priority=0.7,
                description="Enhance natural flow and readability",
                suggested_actions=[
                    "Read translations aloud",
                    "Use native speaker feedback",
                    "Study natural language patterns"
                ],
                estimated_impact=0.12
            ),
            ImprovementArea.CULTURAL_ADAPTATION: QualityImprovement(
                area=area,
                priority=0.6,
                description="Better adapt content to target culture",
                suggested_actions=[
                    "Research target culture context",
                    "Adapt idioms and expressions",
                    "Consider cultural sensitivities"
                ],
                estimated_impact=0.10
            )
        }
        
        return recommendations.get(area, QualityImprovement(
            area=area,
            priority=0.5,
            description="General improvement needed",
            suggested_actions=["Review and refine translation"],
            estimated_impact=0.05
        ))
    
    async def _calculate_confidence(self, result: QualityResult) -> float:
        """Calculate confidence in quality assessment"""
        confidence_factors = []
        
        # Number of metrics used
        metrics_factor = min(1.0, len(result.metric_scores) / 3.0)
        confidence_factors.append(metrics_factor)
        
        # Consistency of scores
        if result.metric_scores:
            scores = list(result.metric_scores.values())
            consistency = 1.0 - statistics.stdev(scores) if len(scores) > 1 else 1.0
            confidence_factors.append(consistency)
        
        # Error analysis depth
        error_factor = min(1.0, len(result.error_analysis) / 5.0)
        confidence_factors.append(error_factor)
        
        return statistics.mean(confidence_factors) if confidence_factors else 0.5
    
    async def _update_error_patterns(self, feedback: HumanFeedback):
        """Update error patterns based on human feedback"""
        for error in feedback.specific_errors:
            pattern_key = f"{error.error_type.value}_{error.location}"
            if pattern_key not in self.error_patterns:
                self.error_patterns[pattern_key] = {"count": 0, "severity_sum": 0.0}
            
            self.error_patterns[pattern_key]["count"] += 1
            self.error_patterns[pattern_key]["severity_sum"] += error.severity
    
    def _hash_text(self, text: str) -> str:
        """Generate hash for text"""
        import hashlib
        return hashlib.md5(text.encode()).hexdigest()
    
    async def get_quality_statistics(self) -> Dict[str, Any]:
        """Get quality assessment statistics"""
        return {
            "assessments_performed": len(self.quality_cache),
            "human_feedback_count": sum(len(feedbacks) for feedbacks in self.feedback_database.values()),
            "error_patterns_identified": len(self.error_patterns),
            "available_metrics": [metric.value for metric in QualityMetric],
            "quality_levels": [level.value for level in QualityLevel],
            "nltk_available": NLTK_AVAILABLE,
            "bert_score_available": BERT_SCORE_AVAILABLE
        }