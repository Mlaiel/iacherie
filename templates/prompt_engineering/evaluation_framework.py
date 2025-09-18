"""
🎯 Evaluation Framework - AI Prompt Quality Assessment System
===========================================================

Enterprise-grade evaluation framework for AI prompt quality with multi-dimensional
scoring, A/B testing, and creator economy performance metrics.

⚠️  PROTECTION INTELLECTUELLE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Tous droits réservés - Usage commercial interdit sans autorisation

Author: Fahed Mlaiel (mlaiel@live.de) - ML Engineer + IA Prompt Engineer + DevOps Expert
Team: Lead Dev IA + Backend Senior + ML Engineer + Security Expert
"""

import asyncio
import logging
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from textstat import flesch_reading_ease, flesch_kincaid_grade
import openai
from transformers import pipeline
from pydantic import BaseModel, Field, validator

from core.config import get_settings
from utils.exceptions import EvaluationError, ValidationError
from .performance_monitor import PerformanceMonitor
from .security_validator import SecurityValidator

logger = logging.getLogger(__name__)
settings = get_settings()


class EvaluationMetric(Enum):
    """Evaluation metric types"""
    RELEVANCE = "relevance"
    COHERENCE = "coherence"
    CREATIVITY = "creativity"
    ACCURACY = "accuracy"
    ENGAGEMENT = "engagement"
    READABILITY = "readability"
    COMPLETENESS = "completeness"
    ORIGINALITY = "originality"
    CREATOR_SATISFACTION = "creator_satisfaction"
    MONETIZATION_POTENTIAL = "monetization_potential"
    COLLABORATION_VALUE = "collaboration_value"
    SEO_EFFECTIVENESS = "seo_effectiveness"
    PLATFORM_OPTIMIZATION = "platform_optimization"
    AUDIENCE_ALIGNMENT = "audience_alignment"


class EvaluationDimension(Enum):
    """Evaluation dimensions"""
    QUALITY = "quality"
    PERFORMANCE = "performance"
    CREATOR_ECONOMY = "creator_economy"
    TECHNICAL = "technical"
    BUSINESS = "business"
    USER_EXPERIENCE = "user_experience"


class ComparisonMethod(Enum):
    """A/B testing comparison methods"""
    HUMAN_EVALUATION = "human_evaluation"
    AUTOMATED_SCORING = "automated_scoring"
    HYBRID_EVALUATION = "hybrid_evaluation"
    CREATOR_FEEDBACK = "creator_feedback"
    AUDIENCE_METRICS = "audience_metrics"


@dataclass
class EvaluationCriteria:
    """Evaluation criteria definition"""
    metric: EvaluationMetric
    weight: float
    threshold: float
    description: str
    evaluation_method: str
    creator_economy_specific: bool = False
    automated: bool = True


@dataclass
class EvaluationResult:
    """Individual evaluation result"""
    metric: EvaluationMetric
    score: float
    confidence: float
    explanation: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ComprehensiveEvaluation:
    """Comprehensive evaluation result"""
    overall_score: float
    dimension_scores: Dict[EvaluationDimension, float]
    metric_results: List[EvaluationResult]
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]
    creator_economy_score: float
    evaluation_timestamp: datetime = field(default_factory=datetime.utcnow)
    evaluation_time_ms: int = 0
    confidence_level: float = 0.0


@dataclass
class ABTestResult:
    """A/B test result"""
    test_id: str
    variant_a_score: float
    variant_b_score: float
    winner: str
    confidence: float
    statistical_significance: bool
    sample_size: int
    effect_size: float
    detailed_metrics: Dict[str, Dict[str, float]]
    creator_feedback: Dict[str, Any] = field(default_factory=dict)


class EvaluationRequest(BaseModel):
    """Evaluation request"""
    prompt: str = Field(..., min_length=1)
    response: str = Field(..., min_length=1)
    template_id: Optional[str] = None
    model_name: Optional[str] = None
    creator_context: Dict[str, Any] = Field(default_factory=dict)
    evaluation_criteria: List[str] = Field(default_factory=list)
    target_audience: Optional[str] = None
    content_category: Optional[str] = None
    expected_outcomes: List[str] = Field(default_factory=list)
    
    @validator('prompt', 'response')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()


class ABTestRequest(BaseModel):
    """A/B test request"""
    test_name: str = Field(..., min_length=1)
    variant_a: Dict[str, str] = Field(...)
    variant_b: Dict[str, str] = Field(...)
    evaluation_criteria: List[str] = Field(default_factory=list)
    creator_context: Dict[str, Any] = Field(default_factory=dict)
    target_metrics: List[str] = Field(default_factory=list)
    duration_hours: int = Field(default=24, ge=1, le=168)  # 1 hour to 1 week
    minimum_sample_size: int = Field(default=50, ge=10)
    
    @validator('variant_a', 'variant_b')
    def validate_variants(cls, v):
        if 'prompt' not in v or 'response' not in v:
            raise ValueError("Variants must contain 'prompt' and 'response'")
        return v


class EvaluationFramework:
    """
    🎯 Enterprise Evaluation Framework
    
    Comprehensive prompt evaluation with:
    - Multi-dimensional quality assessment
    - Creator economy specific metrics
    - Automated and human evaluation
    - A/B testing capabilities
    - Statistical significance testing
    - Performance benchmarking
    - Continuous improvement recommendations
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.performance_monitor = PerformanceMonitor()
        self.security_validator = SecurityValidator()
        self.sentiment_analyzer = None
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.evaluation_models: Dict[str, Any] = {}
        self._active_ab_tests: Dict[str, Dict] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize evaluation framework"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Initialize PostgreSQL connection pool
            self.db_pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=3,
                max_size=10
            )
            
            # Initialize MongoDB connection
            self.mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
            
            # Load evaluation models
            await self._load_evaluation_models()
            
            # Create database tables
            await self._create_tables()
            
            # Initialize components
            await self.performance_monitor.initialize()
            await self.security_validator.initialize()
            
            self._initialized = True
            logger.info("Evaluation Framework initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize Evaluation Framework: {e}")
            raise EvaluationError(f"Evaluation Framework initialization failed: {e}")
    
    async def _load_evaluation_models(self) -> None:
        """Load ML models for automated evaluation"""
        try:
            # Load sentiment analysis model
            try:
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    device=-1  # CPU
                )
            except Exception as e:
                logger.warning(f"Failed to load sentiment analyzer: {e}")
                self.sentiment_analyzer = None
            
            # Load other evaluation models
            # In production, these would be custom-trained models
            self.evaluation_models = {
                "creativity": self._evaluate_creativity,
                "coherence": self._evaluate_coherence,
                "relevance": self._evaluate_relevance,
                "engagement": self._evaluate_engagement,
                "monetization": self._evaluate_monetization_potential,
                "seo": self._evaluate_seo_effectiveness
            }
            
            logger.info("Evaluation models loaded successfully")
        
        except Exception as e:
            logger.error(f"Failed to load evaluation models: {e}")
    
    async def _create_tables(self) -> None:
        """Create evaluation-related database tables"""
        create_evaluations_table = """
        CREATE TABLE IF NOT EXISTS evaluations (
            id SERIAL PRIMARY KEY,
            evaluation_id VARCHAR(255) UNIQUE NOT NULL,
            template_id VARCHAR(255),
            model_name VARCHAR(100),
            prompt_hash VARCHAR(64),
            response_hash VARCHAR(64),
            overall_score FLOAT NOT NULL,
            dimension_scores JSONB,
            metric_results JSONB,
            creator_context JSONB,
            evaluation_time_ms INTEGER,
            confidence_level FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (template_id, created_at),
            INDEX (overall_score, created_at)
        );
        """
        
        create_ab_tests_table = """
        CREATE TABLE IF NOT EXISTS ab_tests (
            id SERIAL PRIMARY KEY,
            test_id VARCHAR(255) UNIQUE NOT NULL,
            test_name VARCHAR(255) NOT NULL,
            variant_a JSONB NOT NULL,
            variant_b JSONB NOT NULL,
            status VARCHAR(50) DEFAULT 'running',
            winner VARCHAR(10),
            confidence FLOAT,
            statistical_significance BOOLEAN,
            sample_size INTEGER DEFAULT 0,
            effect_size FLOAT,
            detailed_metrics JSONB,
            creator_context JSONB,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            duration_hours INTEGER
        );
        """
        
        create_evaluation_feedback_table = """
        CREATE TABLE IF NOT EXISTS evaluation_feedback (
            id SERIAL PRIMARY KEY,
            feedback_id VARCHAR(255) UNIQUE NOT NULL,
            evaluation_id VARCHAR(255) REFERENCES evaluations(evaluation_id),
            feedback_type VARCHAR(50) NOT NULL,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            comments TEXT,
            creator_id VARCHAR(255),
            helpful BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(create_evaluations_table)
            await conn.execute(create_ab_tests_table)
            await conn.execute(create_evaluation_feedback_table)
    
    async def evaluate_prompt_response(self, request: EvaluationRequest) -> ComprehensiveEvaluation:
        """
        Comprehensive evaluation of prompt-response pair
        
        Args:
            request: Evaluation request with prompt, response, and context
            
        Returns:
            Comprehensive evaluation result
        """
        start_time = datetime.utcnow()
        
        try:
            # Define evaluation criteria based on request
            criteria = await self._get_evaluation_criteria(request)
            
            # Run individual metric evaluations
            metric_results = []
            for criterion in criteria:
                result = await self._evaluate_metric(
                    request.prompt,
                    request.response,
                    criterion,
                    request.creator_context
                )
                metric_results.append(result)
            
            # Calculate dimension scores
            dimension_scores = await self._calculate_dimension_scores(metric_results)
            
            # Calculate overall score
            overall_score = await self._calculate_overall_score(metric_results, criteria)
            
            # Calculate creator economy specific score
            creator_economy_score = await self._calculate_creator_economy_score(
                metric_results, request.creator_context
            )
            
            # Identify strengths and weaknesses
            strengths, weaknesses = await self._analyze_strengths_weaknesses(metric_results)
            
            # Generate improvement suggestions
            improvement_suggestions = await self._generate_improvement_suggestions(
                metric_results, request.creator_context
            )
            
            # Calculate confidence level
            confidence_level = await self._calculate_confidence_level(metric_results)
            
            end_time = datetime.utcnow()
            evaluation_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            evaluation = ComprehensiveEvaluation(
                overall_score=overall_score,
                dimension_scores=dimension_scores,
                metric_results=metric_results,
                strengths=strengths,
                weaknesses=weaknesses,
                improvement_suggestions=improvement_suggestions,
                creator_economy_score=creator_economy_score,
                evaluation_time_ms=evaluation_time_ms,
                confidence_level=confidence_level
            )
            
            # Store evaluation result
            await self._store_evaluation(request, evaluation)
            
            return evaluation
        
        except Exception as e:
            logger.error(f"Prompt evaluation failed: {e}")
            raise EvaluationError(f"Prompt evaluation failed: {e}")
    
    async def _get_evaluation_criteria(self, request: EvaluationRequest) -> List[EvaluationCriteria]:
        """Get evaluation criteria based on request"""
        default_criteria = [
            EvaluationCriteria(
                metric=EvaluationMetric.RELEVANCE,
                weight=0.2,
                threshold=0.7,
                description="How well the response addresses the prompt",
                evaluation_method="semantic_similarity"
            ),
            EvaluationCriteria(
                metric=EvaluationMetric.COHERENCE,
                weight=0.15,
                threshold=0.6,
                description="Logical flow and consistency",
                evaluation_method="linguistic_analysis"
            ),
            EvaluationCriteria(
                metric=EvaluationMetric.READABILITY,
                weight=0.1,
                threshold=0.5,
                description="Ease of reading and understanding",
                evaluation_method="readability_metrics"
            ),
            EvaluationCriteria(
                metric=EvaluationMetric.ENGAGEMENT,
                weight=0.15,
                threshold=0.6,
                description="Ability to engage the audience",
                evaluation_method="engagement_analysis"
            )
        ]
        
        # Add creator economy specific criteria
        if request.creator_context.get('creator_type'):
            default_criteria.extend([
                EvaluationCriteria(
                    metric=EvaluationMetric.CREATOR_SATISFACTION,
                    weight=0.15,
                    threshold=0.7,
                    description="Creator satisfaction with output",
                    evaluation_method="creator_feedback",
                    creator_economy_specific=True
                ),
                EvaluationCriteria(
                    metric=EvaluationMetric.MONETIZATION_POTENTIAL,
                    weight=0.1,
                    threshold=0.5,
                    description="Potential for monetization",
                    evaluation_method="monetization_analysis",
                    creator_economy_specific=True
                ),
                EvaluationCriteria(
                    metric=EvaluationMetric.PLATFORM_OPTIMIZATION,
                    weight=0.15,
                    threshold=0.6,
                    description="Optimization for target platforms",
                    evaluation_method="platform_analysis",
                    creator_economy_specific=True
                )
            ])
        
        # Filter by requested criteria if specified
        if request.evaluation_criteria:
            requested_metrics = [EvaluationMetric(metric) for metric in request.evaluation_criteria]
            default_criteria = [c for c in default_criteria if c.metric in requested_metrics]
        
        return default_criteria
    
    async def _evaluate_metric(
        self,
        prompt: str,
        response: str,
        criterion: EvaluationCriteria,
        creator_context: Dict[str, Any]
    ) -> EvaluationResult:
        """Evaluate a single metric"""
        try:
            if criterion.metric in self.evaluation_models:
                score, confidence, explanation, evidence = await self.evaluation_models[criterion.metric](
                    prompt, response, creator_context
                )
            else:
                # Fallback evaluation
                score, confidence, explanation, evidence = await self._fallback_evaluation(
                    prompt, response, criterion, creator_context
                )
            
            # Generate recommendations based on score
            recommendations = await self._generate_metric_recommendations(
                criterion.metric, score, evidence, creator_context
            )
            
            return EvaluationResult(
                metric=criterion.metric,
                score=max(0.0, min(1.0, score)),  # Clamp to [0, 1]
                confidence=confidence,
                explanation=explanation,
                evidence=evidence,
                recommendations=recommendations
            )
        
        except Exception as e:
            logger.error(f"Metric evaluation failed for {criterion.metric}: {e}")
            return EvaluationResult(
                metric=criterion.metric,
                score=0.5,  # Neutral score on error
                confidence=0.0,
                explanation=f"Evaluation failed: {e}",
                evidence={"error": str(e)}
            )
    
    async def _evaluate_creativity(self, prompt: str, response: str, context: Dict[str, Any]) -> Tuple[float, float, str, Dict]:
        """Evaluate creativity of the response"""
        try:
            # Simple creativity heuristics
            unique_words = len(set(response.lower().split()))
            total_words = len(response.split())
            word_diversity = unique_words / total_words if total_words > 0 else 0
            
            # Check for creative indicators
            creative_indicators = [
                'imagine', 'creative', 'innovative', 'unique', 'original',
                'artistic', 'inventive', 'novel', 'fresh', 'inspiring'
            ]
            creative_count = sum(1 for word in creative_indicators if word in response.lower())
            creative_score = min(creative_count / 3, 1.0)  # Normalize
            
            # Combine scores
            creativity_score = (word_diversity * 0.6) + (creative_score * 0.4)
            
            evidence = {
                "word_diversity": word_diversity,
                "creative_indicators": creative_count,
                "unique_words": unique_words,
                "total_words": total_words
            }
            
            explanation = f"Creativity score based on word diversity ({word_diversity:.2f}) and creative language use"
            
            return creativity_score, 0.7, explanation, evidence
        
        except Exception as e:
            logger.error(f"Creativity evaluation failed: {e}")
            return 0.5, 0.0, f"Evaluation failed: {e}", {}
    
    async def _evaluate_coherence(self, prompt: str, response: str, context: Dict[str, Any]) -> Tuple[float, float, str, Dict]:
        """Evaluate coherence and logical flow"""
        try:
            # Simple coherence metrics
            sentences = response.split('.')
            sentence_count = len([s for s in sentences if s.strip()])
            
            # Check for transition words
            transitions = [
                'however', 'moreover', 'furthermore', 'therefore', 'consequently',
                'additionally', 'meanwhile', 'nevertheless', 'thus', 'hence'
            ]
            transition_count = sum(1 for word in transitions if word in response.lower())
            
            # Calculate coherence score
            transition_score = min(transition_count / max(sentence_count / 3, 1), 1.0)
            length_coherence = min(len(response) / 500, 1.0)  # Longer responses tend to be more coherent
            
            coherence_score = (transition_score * 0.4) + (length_coherence * 0.6)
            
            evidence = {
                "sentence_count": sentence_count,
                "transition_words": transition_count,
                "response_length": len(response),
                "transition_score": transition_score
            }
            
            explanation = f"Coherence based on logical flow indicators and response structure"
            
            return coherence_score, 0.8, explanation, evidence
        
        except Exception as e:
            logger.error(f"Coherence evaluation failed: {e}")
            return 0.5, 0.0, f"Evaluation failed: {e}", {}
    
    async def _evaluate_relevance(self, prompt: str, response: str, context: Dict[str, Any]) -> Tuple[float, float, str, Dict]:
        """Evaluate relevance using semantic similarity"""
        try:
            # Simple keyword overlap
            prompt_words = set(prompt.lower().split())
            response_words = set(response.lower().split())
            
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            prompt_words -= stop_words
            response_words -= stop_words
            
            if len(prompt_words) == 0:
                return 0.5, 0.3, "Insufficient prompt content for relevance evaluation", {}
            
            # Calculate overlap
            overlap = len(prompt_words & response_words)
            relevance_score = overlap / len(prompt_words)
            
            # Bonus for addressing prompt directly
            if any(word in response.lower() for word in ['answer', 'respond', 'address', 'solve']):
                relevance_score = min(relevance_score + 0.1, 1.0)
            
            evidence = {
                "prompt_keywords": len(prompt_words),
                "response_keywords": len(response_words),
                "keyword_overlap": overlap,
                "overlap_ratio": overlap / len(prompt_words)
            }
            
            explanation = f"Relevance based on keyword overlap ({overlap}/{len(prompt_words)} keywords matched)"
            
            return relevance_score, 0.7, explanation, evidence
        
        except Exception as e:
            logger.error(f"Relevance evaluation failed: {e}")
            return 0.5, 0.0, f"Evaluation failed: {e}", {}
    
    async def _evaluate_engagement(self, prompt: str, response: str, context: Dict[str, Any]) -> Tuple[float, float, str, Dict]:
        """Evaluate engagement potential"""
        try:
            # Engagement indicators
            engagement_words = [
                'exciting', 'amazing', 'incredible', 'fantastic', 'awesome',
                'interesting', 'compelling', 'engaging', 'captivating', 'fascinating'
            ]
            
            # Question indicators (questions engage readers)
            question_count = response.count('?')
            
            # Call-to-action indicators
            cta_words = ['subscribe', 'follow', 'like', 'share', 'comment', 'join', 'visit']
            cta_count = sum(1 for word in cta_words if word in response.lower())
            
            # Calculate engagement score
            engagement_word_score = min(
                sum(1 for word in engagement_words if word in response.lower()) / 3, 1.0
            )
            question_score = min(question_count / 2, 1.0)
            cta_score = min(cta_count / 2, 1.0)
            
            engagement_score = (engagement_word_score * 0.4) + (question_score * 0.3) + (cta_score * 0.3)
            
            evidence = {
                "engagement_words": sum(1 for word in engagement_words if word in response.lower()),
                "questions": question_count,
                "call_to_actions": cta_count,
                "total_score_components": {
                    "engagement_words": engagement_word_score,
                    "questions": question_score,
                    "cta": cta_score
                }
            }
            
            explanation = f"Engagement score based on engaging language, questions, and CTAs"
            
            return engagement_score, 0.6, explanation, evidence
        
        except Exception as e:
            logger.error(f"Engagement evaluation failed: {e}")
            return 0.5, 0.0, f"Evaluation failed: {e}", {}
    
    async def _evaluate_monetization_potential(self, prompt: str, response: str, context: Dict[str, Any]) -> Tuple[float, float, str, Dict]:
        """Evaluate monetization potential for creators"""
        try:
            # Monetization indicators
            monetization_keywords = [
                'sponsor', 'brand', 'product', 'affiliate', 'partnership',
                'merchandise', 'subscription', 'premium', 'exclusive', 'upgrade'
            ]
            
            # Value proposition indicators
            value_words = [
                'value', 'benefit', 'advantage', 'solution', 'improvement',
                'save', 'earn', 'gain', 'profit', 'investment'
            ]
            
            # Calculate scores
            monetization_score = min(
                sum(1 for word in monetization_keywords if word in response.lower()) / 3, 1.0
            )
            value_score = min(
                sum(1 for word in value_words if word in response.lower()) / 3, 1.0
            )
            
            # Creator context boost
            creator_type = context.get('creator_type', '')
            if creator_type in ['influencer', 'blogger', 'youtuber']:
                monetization_score = min(monetization_score + 0.2, 1.0)
            
            final_score = (monetization_score * 0.6) + (value_score * 0.4)
            
            evidence = {
                "monetization_keywords": sum(1 for word in monetization_keywords if word in response.lower()),
                "value_keywords": sum(1 for word in value_words if word in response.lower()),
                "creator_type": creator_type,
                "creator_boost_applied": creator_type in ['influencer', 'blogger', 'youtuber']
            }
            
            explanation = f"Monetization potential based on commercial language and value propositions"
            
            return final_score, 0.7, explanation, evidence
        
        except Exception as e:
            logger.error(f"Monetization evaluation failed: {e}")
            return 0.5, 0.0, f"Evaluation failed: {e}", {}
    
    async def _evaluate_seo_effectiveness(self, prompt: str, response: str, context: Dict[str, Any]) -> Tuple[float, float, str, Dict]:
        """Evaluate SEO effectiveness"""
        try:
            # SEO indicators
            seo_elements = {
                'keywords': len(set(response.lower().split())) / len(response.split()) if response else 0,
                'length': min(len(response) / 1000, 1.0),  # Optimal length
                'headings': response.count('#') + response.count('**'),  # Markdown headings
                'links': response.count('http'),
                'structure': len(response.split('\n\n'))  # Paragraphs
            }
            
            # Calculate SEO score
            keyword_score = seo_elements['keywords']
            length_score = seo_elements['length']
            structure_score = min(seo_elements['structure'] / 5, 1.0)
            
            seo_score = (keyword_score * 0.4) + (length_score * 0.3) + (structure_score * 0.3)
            
            evidence = seo_elements
            explanation = f"SEO effectiveness based on keyword diversity, content length, and structure"
            
            return seo_score, 0.6, explanation, evidence
        
        except Exception as e:
            logger.error(f"SEO evaluation failed: {e}")
            return 0.5, 0.0, f"Evaluation failed: {e}", {}
    
    async def _fallback_evaluation(
        self,
        prompt: str,
        response: str,
        criterion: EvaluationCriteria,
        context: Dict[str, Any]
    ) -> Tuple[float, float, str, Dict]:
        """Fallback evaluation for unsupported metrics"""
        # Basic heuristic evaluation
        if criterion.metric == EvaluationMetric.READABILITY:
            try:
                reading_ease = flesch_reading_ease(response)
                grade_level = flesch_kincaid_grade(response)
                
                # Normalize scores
                ease_score = max(0, min(reading_ease / 100, 1.0))
                grade_score = max(0, min((12 - grade_level) / 12, 1.0))  # Lower grade = better
                
                readability_score = (ease_score + grade_score) / 2
                
                evidence = {
                    "flesch_reading_ease": reading_ease,
                    "flesch_kincaid_grade": grade_level
                }
                
                explanation = f"Readability score based on Flesch metrics"
                return readability_score, 0.8, explanation, evidence
            except:
                pass
        
        # Default neutral evaluation
        return 0.5, 0.3, f"Basic evaluation for {criterion.metric.value}", {"method": "fallback"}
    
    async def _generate_metric_recommendations(
        self,
        metric: EvaluationMetric,
        score: float,
        evidence: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for improving metric scores"""
        recommendations = []
        
        if score < 0.6:  # Low score threshold
            if metric == EvaluationMetric.RELEVANCE:
                recommendations.extend([
                    "Ensure response directly addresses the prompt",
                    "Include more keywords from the original prompt",
                    "Stay focused on the main topic"
                ])
            
            elif metric == EvaluationMetric.ENGAGEMENT:
                recommendations.extend([
                    "Add more engaging language and enthusiasm",
                    "Include questions to encourage interaction",
                    "Add call-to-action statements"
                ])
            
            elif metric == EvaluationMetric.COHERENCE:
                recommendations.extend([
                    "Use transition words to connect ideas",
                    "Organize content with clear structure",
                    "Ensure logical flow between paragraphs"
                ])
            
            elif metric == EvaluationMetric.MONETIZATION_POTENTIAL:
                recommendations.extend([
                    "Include value propositions for audience",
                    "Consider commercial opportunities",
                    "Add sponsorship or partnership potential"
                ])
        
        return recommendations
    
    async def _calculate_dimension_scores(self, metric_results: List[EvaluationResult]) -> Dict[EvaluationDimension, float]:
        """Calculate scores for each evaluation dimension"""
        dimension_mapping = {
            EvaluationDimension.QUALITY: [
                EvaluationMetric.RELEVANCE, EvaluationMetric.COHERENCE,
                EvaluationMetric.ACCURACY, EvaluationMetric.COMPLETENESS
            ],
            EvaluationDimension.CREATOR_ECONOMY: [
                EvaluationMetric.CREATOR_SATISFACTION, EvaluationMetric.MONETIZATION_POTENTIAL,
                EvaluationMetric.COLLABORATION_VALUE, EvaluationMetric.PLATFORM_OPTIMIZATION
            ],
            EvaluationDimension.USER_EXPERIENCE: [
                EvaluationMetric.ENGAGEMENT, EvaluationMetric.READABILITY,
                EvaluationMetric.AUDIENCE_ALIGNMENT
            ],
            EvaluationDimension.TECHNICAL: [
                EvaluationMetric.SEO_EFFECTIVENESS, EvaluationMetric.ORIGINALITY
            ]
        }
        
        dimension_scores = {}
        
        for dimension, metrics in dimension_mapping.items():
            relevant_results = [r for r in metric_results if r.metric in metrics]
            if relevant_results:
                # Weighted average based on confidence
                total_weight = sum(r.confidence for r in relevant_results)
                if total_weight > 0:
                    weighted_score = sum(r.score * r.confidence for r in relevant_results) / total_weight
                else:
                    weighted_score = sum(r.score for r in relevant_results) / len(relevant_results)
                
                dimension_scores[dimension] = weighted_score
            else:
                dimension_scores[dimension] = 0.5  # Neutral score if no metrics
        
        return dimension_scores
    
    async def _calculate_overall_score(
        self,
        metric_results: List[EvaluationResult],
        criteria: List[EvaluationCriteria]
    ) -> float:
        """Calculate overall evaluation score"""
        if not metric_results:
            return 0.5
        
        # Create weight mapping
        weight_mapping = {c.metric: c.weight for c in criteria}
        
        total_weight = 0
        weighted_sum = 0
        
        for result in metric_results:
            weight = weight_mapping.get(result.metric, 1.0)
            confidence_weight = weight * result.confidence
            
            weighted_sum += result.score * confidence_weight
            total_weight += confidence_weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.5
    
    async def _calculate_creator_economy_score(
        self,
        metric_results: List[EvaluationResult],
        context: Dict[str, Any]
    ) -> float:
        """Calculate creator economy specific score"""
        creator_metrics = [
            EvaluationMetric.CREATOR_SATISFACTION,
            EvaluationMetric.MONETIZATION_POTENTIAL,
            EvaluationMetric.COLLABORATION_VALUE,
            EvaluationMetric.PLATFORM_OPTIMIZATION
        ]
        
        relevant_results = [r for r in metric_results if r.metric in creator_metrics]
        
        if not relevant_results:
            return 0.5
        
        # Weight by confidence
        total_confidence = sum(r.confidence for r in relevant_results)
        if total_confidence > 0:
            return sum(r.score * r.confidence for r in relevant_results) / total_confidence
        else:
            return sum(r.score for r in relevant_results) / len(relevant_results)
    
    async def _analyze_strengths_weaknesses(self, metric_results: List[EvaluationResult]) -> Tuple[List[str], List[str]]:
        """Analyze strengths and weaknesses from metric results"""
        strengths = []
        weaknesses = []
        
        for result in metric_results:
            if result.score >= 0.8:
                strengths.append(f"Excellent {result.metric.value.replace('_', ' ')}")
            elif result.score <= 0.4:
                weaknesses.append(f"Needs improvement in {result.metric.value.replace('_', ' ')}")
        
        return strengths, weaknesses
    
    async def _generate_improvement_suggestions(
        self,
        metric_results: List[EvaluationResult],
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Collect recommendations from low-scoring metrics
        for result in metric_results:
            if result.score < 0.6:
                suggestions.extend(result.recommendations)
        
        # Add context-specific suggestions
        creator_type = context.get('creator_type')
        if creator_type:
            if creator_type == "musician" and any(r.metric == EvaluationMetric.ENGAGEMENT and r.score < 0.6 for r in metric_results):
                suggestions.append("Consider adding music-specific engagement elements")
            elif creator_type == "blogger" and any(r.metric == EvaluationMetric.SEO_EFFECTIVENESS and r.score < 0.6 for r in metric_results):
                suggestions.append("Optimize content for SEO with better keyword usage")
        
        return list(set(suggestions))  # Remove duplicates
    
    async def _calculate_confidence_level(self, metric_results: List[EvaluationResult]) -> float:
        """Calculate overall confidence in evaluation"""
        if not metric_results:
            return 0.0
        
        return sum(r.confidence for r in metric_results) / len(metric_results)
    
    async def _store_evaluation(self, request: EvaluationRequest, evaluation: ComprehensiveEvaluation) -> None:
        """Store evaluation result in database"""
        try:
            import hashlib
            
            evaluation_id = f"eval_{int(datetime.utcnow().timestamp())}"
            prompt_hash = hashlib.sha256(request.prompt.encode()).hexdigest()
            response_hash = hashlib.sha256(request.response.encode()).hexdigest()
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO evaluations 
                    (evaluation_id, template_id, model_name, prompt_hash, response_hash,
                     overall_score, dimension_scores, metric_results, creator_context,
                     evaluation_time_ms, confidence_level)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """, evaluation_id, request.template_id, request.model_name,
                    prompt_hash, response_hash, evaluation.overall_score,
                    json.dumps({k.value: v for k, v in evaluation.dimension_scores.items()}),
                    json.dumps([{
                        "metric": r.metric.value,
                        "score": r.score,
                        "confidence": r.confidence,
                        "explanation": r.explanation
                    } for r in evaluation.metric_results]),
                    json.dumps(request.creator_context),
                    evaluation.evaluation_time_ms, evaluation.confidence_level)
        
        except Exception as e:
            logger.error(f"Failed to store evaluation: {e}")
    
    async def start_ab_test(self, request: ABTestRequest) -> str:
        """Start an A/B test between two prompt variants"""
        try:
            test_id = f"ab_{int(datetime.utcnow().timestamp())}"
            
            # Store A/B test configuration
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO ab_tests 
                    (test_id, test_name, variant_a, variant_b, creator_context, duration_hours)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, test_id, request.test_name,
                    json.dumps(request.variant_a), json.dumps(request.variant_b),
                    json.dumps(request.creator_context), request.duration_hours)
            
            # Add to active tests
            self._active_ab_tests[test_id] = {
                "start_time": datetime.utcnow(),
                "duration_hours": request.duration_hours,
                "variant_a_results": [],
                "variant_b_results": [],
                "minimum_sample_size": request.minimum_sample_size
            }
            
            logger.info(f"Started A/B test: {test_id}")
            return test_id
        
        except Exception as e:
            logger.error(f"Failed to start A/B test: {e}")
            raise EvaluationError(f"A/B test start failed: {e}")
    
    async def get_evaluation_summary(self, template_id: str, days: int = 30) -> Dict[str, Any]:
        """Get evaluation summary for a template"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_evaluations,
                        AVG(overall_score) as avg_score,
                        MAX(overall_score) as best_score,
                        MIN(overall_score) as worst_score,
                        AVG(confidence_level) as avg_confidence
                    FROM evaluations 
                    WHERE template_id = $1 AND created_at >= $2
                """, template_id, cutoff_date)
                
                return dict(row) if row else {}
        
        except Exception as e:
            logger.error(f"Failed to get evaluation summary: {e}")
            return {}
    
    async def cleanup(self) -> None:
        """Cleanup evaluation framework resources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.db_pool:
                await self.db_pool.close()
            
            if self.mongo_client:
                self.mongo_client.close()
            
            logger.info("Evaluation Framework cleanup completed")
        
        except Exception as e:
            logger.error(f"Evaluation Framework cleanup failed: {e}")


# Global evaluation framework instance
evaluation_framework = EvaluationFramework()