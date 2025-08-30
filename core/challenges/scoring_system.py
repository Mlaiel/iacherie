"""
Challenge Scoring System - Advanced Multi-Dimensional Scoring Engine

This module provides sophisticated scoring algorithms for challenge evaluation,
incorporating AI-powered assessment, business value calculation, and creator
performance analytics with real-time scoring optimization.

Features:
- Multi-dimensional scoring with weighted algorithms
- AI-powered content quality assessment
- Real-time performance tracking and optimization
- Business value and monetization impact scoring
- Creator collaboration compatibility scoring
- Dynamic scoring model adaptation
- Professional scoring transparency and auditability
- Integration with creator growth analytics

Business Logic Integration:
- Challenge submission → Multi-dimensional scoring → Performance ranking
- Scoring results → Creator matching → Collaboration opportunities
- Business impact scoring → Revenue optimization → Monetization tracking

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code, concept, and intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, distribution, or theft of this code or concept
without explicit written permission from Fahed Mlaiel is strictly prohibited
and will result in immediate legal action.

Contact: mlaiel@live.de for authorized usage inquiries.
"""

from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import asyncio
import json
import logging
import math
import statistics
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ScoringMethod(Enum):
    """Professional scoring methodology options"""
    WEIGHTED_AVERAGE = "weighted_average"
    POINTS_BASED = "points_based"
    PERCENTILE_RANKING = "percentile_ranking"
    AI_EVALUATION = "ai_evaluation"
    HYBRID_SCORING = "hybrid_scoring"
    BUSINESS_VALUE = "business_value"
    PEER_EVALUATION = "peer_evaluation"
    EXPERT_REVIEW = "expert_review"


class ScoreCategory(Enum):
    """Score category classification"""
    CONTENT_QUALITY = "content_quality"
    CREATIVITY = "creativity"
    TECHNICAL_EXECUTION = "technical_execution"
    BUSINESS_IMPACT = "business_impact"
    AUDIENCE_ENGAGEMENT = "audience_engagement"
    COLLABORATION_POTENTIAL = "collaboration_potential"
    INNOVATION = "innovation"
    SEO_OPTIMIZATION = "seo_optimization"
    MONETIZATION_VALUE = "monetization_value"
    PLATFORM_COMPLIANCE = "platform_compliance"


class ScoreWeightType(Enum):
    """Score weight calculation types"""
    STATIC = "static"
    DYNAMIC = "dynamic"
    ADAPTIVE = "adaptive"
    PERFORMANCE_BASED = "performance_based"


@dataclass
class ScoringCriterion:
    """Individual scoring criterion specification"""
    criterion_id: str
    name: str
    description: str
    category: ScoreCategory
    weight: float
    max_score: float = 100.0
    min_score: float = 0.0
    weight_type: ScoreWeightType = ScoreWeightType.STATIC
    calculation_method: str = "linear"
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScoringConfiguration:
    """Comprehensive scoring system configuration"""
    config_id: str
    name: str
    description: str
    scoring_method: ScoringMethod
    
    # Criteria and weights
    criteria: List[ScoringCriterion] = field(default_factory=list)
    global_weights: Dict[ScoreCategory, float] = field(default_factory=dict)
    
    # Normalization and scaling
    normalization_enabled: bool = True
    score_scaling_factor: float = 1.0
    outlier_handling: str = "cap"  # cap, remove, adjust
    
    # AI integration
    ai_evaluation_enabled: bool = False
    ai_confidence_threshold: float = 0.8
    ai_model_version: str = "v1.0"
    
    # Business logic
    business_value_weight: float = 0.3
    quality_threshold: float = 70.0
    performance_bonus_enabled: bool = True
    
    # Configuration
    version: str = "1.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScoreResult:
    """Comprehensive scoring result with detailed breakdown"""
    submission_id: str
    scorer_id: str
    scoring_timestamp: datetime
    
    # Overall scores
    final_score: float
    normalized_score: float
    percentile_rank: float
    
    # Category scores
    category_scores: Dict[ScoreCategory, float] = field(default_factory=dict)
    criterion_scores: Dict[str, float] = field(default_factory=dict)
    
    # Analysis
    strengths: List[str] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Business metrics
    business_value_score: float = 0.0
    monetization_potential: float = 0.0
    collaboration_compatibility: float = 0.0
    
    # Quality assurance
    confidence_score: float = 1.0
    validation_status: str = "valid"
    reviewer_notes: str = ""
    
    # Performance tracking
    scoring_duration_ms: float = 0.0
    model_version: str = ""
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScoringAnalytics:
    """Scoring system analytics and performance metrics"""
    total_submissions_scored: int = 0
    average_score: float = 0.0
    score_distribution: Dict[str, int] = field(default_factory=dict)
    category_performance: Dict[ScoreCategory, Dict[str, float]] = field(default_factory=dict)
    scoring_time_metrics: Dict[str, float] = field(default_factory=dict)
    accuracy_metrics: Dict[str, float] = field(default_factory=dict)


class ScoringAlgorithm(ABC):
    """Abstract base class for scoring algorithms"""
    
    @abstractmethod
    async def calculate_score(
        self,
        submission_data: Dict[str, Any],
        configuration: ScoringConfiguration,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """Calculate scores for submission"""
        pass
    
    @abstractmethod
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Get algorithm information and parameters"""
        pass


class WeightedAverageScorer(ScoringAlgorithm):
    """Weighted average scoring algorithm"""
    
    async def calculate_score(
        self,
        submission_data: Dict[str, Any],
        configuration: ScoringConfiguration,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """Calculate weighted average scores"""
        try:
            scores = {}
            total_weight = 0.0
            weighted_sum = 0.0
            
            for criterion in configuration.criteria:
                # Get raw value from submission
                raw_value = submission_data.get(criterion.criterion_id, 0.0)
                
                # Calculate criterion score
                criterion_score = await self._calculate_criterion_score(
                    raw_value, criterion, submission_data
                )
                
                scores[criterion.criterion_id] = criterion_score
                
                # Apply weight
                weight = await self._get_dynamic_weight(criterion, context)
                weighted_sum += criterion_score * weight
                total_weight += weight
            
            # Calculate final weighted average
            if total_weight > 0:
                final_score = weighted_sum / total_weight
            else:
                final_score = 0.0
            
            scores['final_score'] = final_score
            return scores
            
        except Exception as e:
            logger.error(f"Error in weighted average scoring: {e}")
            return {'final_score': 0.0}
    
    async def _calculate_criterion_score(
        self,
        raw_value: Union[int, float, str],
        criterion: ScoringCriterion,
        submission_data: Dict[str, Any]
    ) -> float:
        """Calculate score for individual criterion"""
        try:
            if criterion.calculation_method == "linear":
                # Linear scaling
                if isinstance(raw_value, (int, float)):
                    max_possible = criterion.parameters.get('max_value', 100.0)
                    if max_possible > 0:
                        score = (raw_value / max_possible) * criterion.max_score
                    else:
                        score = criterion.max_score if raw_value > 0 else 0.0
                else:
                    score = criterion.max_score if raw_value else 0.0
            
            elif criterion.calculation_method == "logarithmic":
                # Logarithmic scaling for metrics with diminishing returns
                if isinstance(raw_value, (int, float)) and raw_value > 0:
                    base_value = criterion.parameters.get('base_value', 1.0)
                    score = criterion.max_score * math.log(raw_value + base_value) / math.log(100 + base_value)
                else:
                    score = 0.0
            
            elif criterion.calculation_method == "exponential":
                # Exponential scaling for high-impact metrics
                if isinstance(raw_value, (int, float)):
                    growth_factor = criterion.parameters.get('growth_factor', 0.1)
                    score = criterion.max_score * (1 - math.exp(-growth_factor * raw_value))
                else:
                    score = 0.0
            
            else:
                # Default to linear
                score = min(criterion.max_score, max(criterion.min_score, float(raw_value)))
            
            # Clamp to bounds
            return max(criterion.min_score, min(criterion.max_score, score))
            
        except Exception as e:
            logger.error(f"Error calculating criterion score: {e}")
            return criterion.min_score
    
    async def _get_dynamic_weight(
        self,
        criterion: ScoringCriterion,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Get dynamic weight based on context"""
        base_weight = criterion.weight
        
        if criterion.weight_type == ScoreWeightType.STATIC:
            return base_weight
        
        if not context:
            return base_weight
        
        # Dynamic weight adjustment
        if criterion.weight_type == ScoreWeightType.DYNAMIC:
            # Adjust based on challenge type
            challenge_type = context.get('challenge_type', 'content_creation')
            
            if challenge_type == 'collaboration' and criterion.category == ScoreCategory.COLLABORATION_POTENTIAL:
                return base_weight * 1.5
            elif challenge_type == 'monetization' and criterion.category == ScoreCategory.BUSINESS_IMPACT:
                return base_weight * 1.3
        
        elif criterion.weight_type == ScoreWeightType.PERFORMANCE_BASED:
            # Adjust based on historical performance
            avg_performance = context.get('category_avg_performance', {}).get(criterion.category.value, 0.5)
            if avg_performance < 0.3:
                return base_weight * 1.2  # Emphasize weak areas
        
        return base_weight
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Get algorithm information"""
        return {
            'name': 'Weighted Average Scorer',
            'version': '1.0',
            'description': 'Calculates weighted average scores across multiple criteria',
            'supported_methods': ['linear', 'logarithmic', 'exponential'],
            'features': ['dynamic_weights', 'context_awareness', 'normalization']
        }


class AIEvaluationScorer(ScoringAlgorithm):
    """AI-powered evaluation scoring algorithm"""
    
    def __init__(self, ai_config: Dict[str, Any]):
        self.ai_config = ai_config
        self.model_weights = {
            ScoreCategory.CONTENT_QUALITY: 0.25,
            ScoreCategory.CREATIVITY: 0.20,
            ScoreCategory.TECHNICAL_EXECUTION: 0.15,
            ScoreCategory.AUDIENCE_ENGAGEMENT: 0.20,
            ScoreCategory.BUSINESS_IMPACT: 0.20
        }
    
    async def calculate_score(
        self,
        submission_data: Dict[str, Any],
        configuration: ScoringConfiguration,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """Calculate AI-powered evaluation scores"""
        try:
            scores = {}
            
            # Extract content for AI analysis
            content_data = submission_data.get('content_data', {})
            media_files = submission_data.get('media_files', [])
            metadata = submission_data.get('metadata', {})
            
            # AI evaluation for each category
            for category in ScoreCategory:
                category_score = await self._evaluate_category_with_ai(
                    category, content_data, media_files, metadata
                )
                scores[f'ai_{category.value}'] = category_score
            
            # Calculate weighted final score
            final_score = sum(
                scores[f'ai_{category.value}'] * self.model_weights.get(category, 0.1)
                for category in ScoreCategory
                if f'ai_{category.value}' in scores
            )
            
            scores['ai_final_score'] = final_score
            scores['ai_confidence'] = await self._calculate_confidence(scores)
            
            return scores
            
        except Exception as e:
            logger.error(f"Error in AI evaluation scoring: {e}")
            return {'ai_final_score': 0.0, 'ai_confidence': 0.0}
    
    async def _evaluate_category_with_ai(
        self,
        category: ScoreCategory,
        content_data: Dict[str, Any],
        media_files: List[str],
        metadata: Dict[str, Any]
    ) -> float:
        """Evaluate specific category using AI models"""
        try:
            # Simulate AI evaluation (in production, integrate with actual AI services)
            
            if category == ScoreCategory.CONTENT_QUALITY:
                return await self._evaluate_content_quality(content_data, media_files)
            elif category == ScoreCategory.CREATIVITY:
                return await self._evaluate_creativity(content_data, metadata)
            elif category == ScoreCategory.TECHNICAL_EXECUTION:
                return await self._evaluate_technical_execution(media_files, metadata)
            elif category == ScoreCategory.AUDIENCE_ENGAGEMENT:
                return await self._evaluate_engagement_potential(content_data, metadata)
            elif category == ScoreCategory.BUSINESS_IMPACT:
                return await self._evaluate_business_impact(content_data, metadata)
            else:
                # Default evaluation
                return 75.0
                
        except Exception as e:
            logger.error(f"Error evaluating category {category}: {e}")
            return 50.0
    
    async def _evaluate_content_quality(
        self,
        content_data: Dict[str, Any],
        media_files: List[str]
    ) -> float:
        """AI evaluation of content quality"""
        # Placeholder for AI content quality assessment
        base_score = 70.0
        
        # Adjust based on content characteristics
        if content_data.get('description'):
            description_length = len(content_data['description'])
            base_score += min(20.0, description_length / 50)  # Bonus for detailed descriptions
        
        if media_files:
            base_score += min(10.0, len(media_files) * 2)  # Bonus for media content
        
        return min(100.0, max(0.0, base_score))
    
    async def _evaluate_creativity(
        self,
        content_data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> float:
        """AI evaluation of creativity"""
        # Placeholder for AI creativity assessment
        base_score = 65.0
        
        # Adjust based on creative elements
        tags = content_data.get('tags', [])
        if len(tags) > 3:
            base_score += min(15.0, len(tags) * 2)
        
        # Check for innovative elements
        if metadata.get('has_original_elements'):
            base_score += 15.0
        
        return min(100.0, max(0.0, base_score))
    
    async def _evaluate_technical_execution(
        self,
        media_files: List[str],
        metadata: Dict[str, Any]
    ) -> float:
        """AI evaluation of technical execution"""
        # Placeholder for AI technical assessment
        base_score = 75.0
        
        # Check technical quality indicators
        resolution = metadata.get('resolution', {})
        if resolution.get('width', 0) >= 1920:
            base_score += 10.0
        
        if metadata.get('audio_quality', 'standard') == 'high':
            base_score += 10.0
        
        return min(100.0, max(0.0, base_score))
    
    async def _evaluate_engagement_potential(
        self,
        content_data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> float:
        """AI evaluation of engagement potential"""
        # Placeholder for AI engagement assessment
        base_score = 70.0
        
        # Check engagement factors
        if content_data.get('call_to_action'):
            base_score += 10.0
        
        engagement_elements = metadata.get('engagement_elements', 0)
        base_score += min(15.0, engagement_elements * 3)
        
        return min(100.0, max(0.0, base_score))
    
    async def _evaluate_business_impact(
        self,
        content_data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> float:
        """AI evaluation of business impact"""
        # Placeholder for AI business impact assessment
        base_score = 60.0
        
        # Check monetization potential
        monetization_elements = metadata.get('monetization_elements', 0)
        base_score += min(20.0, monetization_elements * 5)
        
        if metadata.get('brand_safe', True):
            base_score += 15.0
        
        return min(100.0, max(0.0, base_score))
    
    async def _calculate_confidence(self, scores: Dict[str, float]) -> float:
        """Calculate AI confidence score"""
        ai_scores = [v for k, v in scores.items() if k.startswith('ai_') and k != 'ai_final_score']
        
        if not ai_scores:
            return 0.0
        
        # Calculate confidence based on score consistency
        if len(ai_scores) > 1:
            score_variance = statistics.variance(ai_scores)
            # Lower variance = higher confidence
            confidence = max(0.0, 1.0 - (score_variance / 1000))
        else:
            confidence = 0.8  # Default confidence for single score
        
        return min(1.0, confidence)
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Get algorithm information"""
        return {
            'name': 'AI Evaluation Scorer',
            'version': '1.0',
            'description': 'AI-powered multi-dimensional content evaluation',
            'supported_categories': [cat.value for cat in ScoreCategory],
            'features': ['deep_learning', 'content_analysis', 'confidence_scoring']
        }


class BusinessValueScorer(ScoringAlgorithm):
    """Business value and monetization impact scoring"""
    
    def __init__(self):
        self.value_weights = {
            'revenue_potential': 0.35,
            'engagement_value': 0.25,
            'collaboration_value': 0.20,
            'growth_potential': 0.20
        }
    
    async def calculate_score(
        self,
        submission_data: Dict[str, Any],
        configuration: ScoringConfiguration,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """Calculate business value scores"""
        try:
            scores = {}
            
            # Revenue potential assessment
            revenue_score = await self._assess_revenue_potential(submission_data)
            scores['revenue_potential'] = revenue_score
            
            # Engagement value assessment
            engagement_score = await self._assess_engagement_value(submission_data)
            scores['engagement_value'] = engagement_score
            
            # Collaboration value assessment
            collaboration_score = await self._assess_collaboration_value(submission_data)
            scores['collaboration_value'] = collaboration_score
            
            # Growth potential assessment
            growth_score = await self._assess_growth_potential(submission_data)
            scores['growth_potential'] = growth_score
            
            # Calculate weighted business value score
            business_value = sum(
                scores[metric] * weight
                for metric, weight in self.value_weights.items()
                if metric in scores
            )
            
            scores['business_value_score'] = business_value
            return scores
            
        except Exception as e:
            logger.error(f"Error in business value scoring: {e}")
            return {'business_value_score': 0.0}
    
    async def _assess_revenue_potential(self, submission_data: Dict[str, Any]) -> float:
        """Assess revenue generation potential"""
        base_score = 50.0
        
        # Monetization indicators
        monetization_data = submission_data.get('monetization_data', {})
        
        if monetization_data.get('sponsorship_ready'):
            base_score += 20.0
        
        if monetization_data.get('product_placement_suitable'):
            base_score += 15.0
        
        if monetization_data.get('subscription_worthy'):
            base_score += 15.0
        
        return min(100.0, base_score)
    
    async def _assess_engagement_value(self, submission_data: Dict[str, Any]) -> float:
        """Assess audience engagement value"""
        base_score = 60.0
        
        engagement_metrics = submission_data.get('engagement_metrics', {})
        
        predicted_engagement = engagement_metrics.get('predicted_engagement_rate', 0.0)
        base_score += min(30.0, predicted_engagement * 300)  # Scale to 30 max bonus
        
        if engagement_metrics.get('viral_potential', False):
            base_score += 10.0
        
        return min(100.0, base_score)
    
    async def _assess_collaboration_value(self, submission_data: Dict[str, Any]) -> float:
        """Assess collaboration potential value"""
        base_score = 55.0
        
        collaboration_data = submission_data.get('collaboration_data', {})
        
        match_scores = collaboration_data.get('potential_matches', [])
        if match_scores:
            avg_match_score = sum(match_scores) / len(match_scores)
            base_score += min(25.0, avg_match_score / 4)
        
        if collaboration_data.get('cross_platform_suitable'):
            base_score += 20.0
        
        return min(100.0, base_score)
    
    async def _assess_growth_potential(self, submission_data: Dict[str, Any]) -> float:
        """Assess growth and scalability potential"""
        base_score = 65.0
        
        growth_indicators = submission_data.get('growth_indicators', {})
        
        if growth_indicators.get('trend_alignment'):
            base_score += 15.0
        
        if growth_indicators.get('scalability_high'):
            base_score += 15.0
        
        audience_expansion = growth_indicators.get('audience_expansion_potential', 0.0)
        base_score += min(10.0, audience_expansion * 100)
        
        return min(100.0, base_score)
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Get algorithm information"""
        return {
            'name': 'Business Value Scorer',
            'version': '1.0',
            'description': 'Evaluates monetization and business growth potential',
            'metrics': list(self.value_weights.keys()),
            'features': ['revenue_assessment', 'growth_analysis', 'collaboration_value']
        }


class ChallengeScoringSystem:
    """
    Enterprise-grade challenge scoring system with multi-algorithm support
    
    Provides comprehensive scoring capabilities with AI integration, business
    value assessment, and real-time performance analytics.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize scoring system with configuration"""
        self.config = config or {}
        
        # Core storage
        self._scoring_configurations: Dict[str, ScoringConfiguration] = {}
        self._score_history: Dict[str, List[ScoreResult]] = {}
        self._analytics: Dict[str, ScoringAnalytics] = {}
        
        # Scoring algorithms
        self._algorithms: Dict[ScoringMethod, ScoringAlgorithm] = {
            ScoringMethod.WEIGHTED_AVERAGE: WeightedAverageScorer(),
            ScoringMethod.AI_EVALUATION: AIEvaluationScorer(
                self.config.get('ai_config', {})
            ),
            ScoringMethod.BUSINESS_VALUE: BusinessValueScorer()
        }
        
        # Performance tracking
        self._performance_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.default_config_id = self.config.get('default_config_id', 'default')
        self.enable_caching = self.config.get('enable_caching', True)
        self.cache_duration_minutes = self.config.get('cache_duration_minutes', 30)
        
        # Initialize default configuration
        self._initialize_default_configuration()
        
        logger.info("Challenge Scoring System initialized successfully")
    
    async def score_submission(
        self,
        submission_id: str,
        submission_data: Dict[str, Any],
        config_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ScoreResult:
        """Score a challenge submission"""
        try:
            start_time = datetime.now(timezone.utc)
            
            # Get scoring configuration
            config_id = config_id or self.default_config_id
            if config_id not in self._scoring_configurations:
                raise ValueError(f"Scoring configuration {config_id} not found")
            
            configuration = self._scoring_configurations[config_id]
            
            # Get appropriate algorithm
            algorithm = self._algorithms.get(configuration.scoring_method)
            if not algorithm:
                raise ValueError(f"Scoring algorithm {configuration.scoring_method} not available")
            
            # Calculate scores
            raw_scores = await algorithm.calculate_score(submission_data, configuration, context)
            
            # Process and normalize scores
            processed_scores = await self._process_scores(raw_scores, configuration)
            
            # Calculate category scores
            category_scores = await self._calculate_category_scores(
                processed_scores, configuration
            )
            
            # Calculate business metrics
            business_metrics = await self._calculate_business_metrics(
                submission_data, processed_scores
            )
            
            # Generate analysis and recommendations
            analysis = await self._generate_score_analysis(
                processed_scores, category_scores, configuration
            )
            
            # Calculate execution time
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            # Create score result
            result = ScoreResult(
                submission_id=submission_id,
                scorer_id=config_id,
                scoring_timestamp=start_time,
                final_score=processed_scores.get('final_score', 0.0),
                normalized_score=processed_scores.get('normalized_score', 0.0),
                percentile_rank=0.0,  # Will be calculated after storing
                category_scores=category_scores,
                criterion_scores=processed_scores,
                strengths=analysis['strengths'],
                improvement_areas=analysis['improvement_areas'],
                recommendations=analysis['recommendations'],
                business_value_score=business_metrics['business_value'],
                monetization_potential=business_metrics['monetization_potential'],
                collaboration_compatibility=business_metrics['collaboration_compatibility'],
                confidence_score=processed_scores.get('confidence', 1.0),
                validation_status="valid",
                scoring_duration_ms=execution_time,
                model_version=configuration.version
            )
            
            # Store result
            await self._store_score_result(result)
            
            # Update analytics
            await self._update_analytics(config_id, result)
            
            logger.info(f"Submission {submission_id} scored: {result.final_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error scoring submission {submission_id}: {e}")
            raise
    
    async def create_scoring_configuration(
        self,
        config: ScoringConfiguration
    ) -> bool:
        """Create new scoring configuration"""
        try:
            if config.config_id in self._scoring_configurations:
                logger.warning(f"Configuration {config.config_id} already exists")
                return False
            
            # Validate configuration
            validation_result = await self._validate_scoring_configuration(config)
            if not validation_result['valid']:
                logger.error(f"Invalid configuration: {validation_result['errors']}")
                return False
            
            # Store configuration
            self._scoring_configurations[config.config_id] = config
            self._analytics[config.config_id] = ScoringAnalytics()
            
            logger.info(f"Scoring configuration {config.config_id} created")
            return True
            
        except Exception as e:
            logger.error(f"Error creating scoring configuration: {e}")
            return False
    
    async def get_score_analytics(
        self,
        config_id: str,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive scoring analytics"""
        try:
            if config_id not in self._analytics:
                return {}
            
            analytics = self._analytics[config_id]
            score_history = self._score_history.get(config_id, [])
            
            # Filter by time range if specified
            if time_range:
                start_time, end_time = time_range
                score_history = [
                    result for result in score_history
                    if start_time <= result.scoring_timestamp <= end_time
                ]
            
            if not score_history:
                return {'message': 'No data available for specified criteria'}
            
            # Calculate comprehensive analytics
            scores = [result.final_score for result in score_history]
            
            analytics_data = {
                'summary': {
                    'total_submissions': len(score_history),
                    'average_score': statistics.mean(scores) if scores else 0.0,
                    'median_score': statistics.median(scores) if scores else 0.0,
                    'std_deviation': statistics.stdev(scores) if len(scores) > 1 else 0.0,
                    'min_score': min(scores) if scores else 0.0,
                    'max_score': max(scores) if scores else 0.0
                },
                'distribution': await self._calculate_score_distribution(scores),
                'category_analysis': await self._analyze_category_performance(score_history),
                'trends': await self._analyze_scoring_trends(score_history),
                'business_impact': await self._analyze_business_impact(score_history),
                'performance_metrics': {
                    'average_scoring_time_ms': statistics.mean([
                        result.scoring_duration_ms for result in score_history
                    ]) if score_history else 0.0,
                    'average_confidence': statistics.mean([
                        result.confidence_score for result in score_history
                    ]) if score_history else 0.0
                }
            }
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Error getting score analytics: {e}")
            return {}
    
    async def get_leaderboard(
        self,
        config_id: str,
        limit: int = 50,
        category: Optional[ScoreCategory] = None
    ) -> List[Dict[str, Any]]:
        """Get scoring leaderboard"""
        try:
            score_history = self._score_history.get(config_id, [])
            
            if not score_history:
                return []
            
            # Filter by category if specified
            if category:
                # Sort by category score
                score_history.sort(
                    key=lambda x: x.category_scores.get(category, 0.0),
                    reverse=True
                )
                score_field = 'category_score'
            else:
                # Sort by final score
                score_history.sort(key=lambda x: x.final_score, reverse=True)
                score_field = 'final_score'
            
            # Build leaderboard
            leaderboard = []
            for i, result in enumerate(score_history[:limit]):
                entry = {
                    'rank': i + 1,
                    'submission_id': result.submission_id,
                    'score': result.category_scores.get(category, 0.0) if category else result.final_score,
                    'final_score': result.final_score,
                    'normalized_score': result.normalized_score,
                    'percentile_rank': result.percentile_rank,
                    'scoring_timestamp': result.scoring_timestamp.isoformat(),
                    'business_value': result.business_value_score,
                    'confidence': result.confidence_score
                }
                
                if category:
                    entry['category'] = category.value
                    entry['category_score'] = result.category_scores.get(category, 0.0)
                
                leaderboard.append(entry)
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    # Helper methods
    
    def _initialize_default_configuration(self) -> None:
        """Initialize default scoring configuration"""
        try:
            default_criteria = [
                ScoringCriterion(
                    criterion_id="content_quality",
                    name="Content Quality",
                    description="Overall quality and polish of the content",
                    category=ScoreCategory.CONTENT_QUALITY,
                    weight=0.25,
                    calculation_method="linear"
                ),
                ScoringCriterion(
                    criterion_id="creativity",
                    name="Creativity and Originality",
                    description="Creative elements and original thinking",
                    category=ScoreCategory.CREATIVITY,
                    weight=0.20,
                    calculation_method="linear"
                ),
                ScoringCriterion(
                    criterion_id="technical_execution",
                    name="Technical Execution",
                    description="Technical quality and production value",
                    category=ScoreCategory.TECHNICAL_EXECUTION,
                    weight=0.15,
                    calculation_method="linear"
                ),
                ScoringCriterion(
                    criterion_id="business_impact",
                    name="Business Impact",
                    description="Potential business and monetization impact",
                    category=ScoreCategory.BUSINESS_IMPACT,
                    weight=0.25,
                    calculation_method="linear"
                ),
                ScoringCriterion(
                    criterion_id="audience_engagement",
                    name="Audience Engagement",
                    description="Potential for audience engagement and interaction",
                    category=ScoreCategory.AUDIENCE_ENGAGEMENT,
                    weight=0.15,
                    calculation_method="linear"
                )
            ]
            
            default_config = ScoringConfiguration(
                config_id=self.default_config_id,
                name="Default Challenge Scoring",
                description="Standard scoring configuration for challenge submissions",
                scoring_method=ScoringMethod.WEIGHTED_AVERAGE,
                criteria=default_criteria,
                global_weights={
                    ScoreCategory.CONTENT_QUALITY: 0.25,
                    ScoreCategory.CREATIVITY: 0.20,
                    ScoreCategory.TECHNICAL_EXECUTION: 0.15,
                    ScoreCategory.BUSINESS_IMPACT: 0.25,
                    ScoreCategory.AUDIENCE_ENGAGEMENT: 0.15
                }
            )
            
            self._scoring_configurations[self.default_config_id] = default_config
            self._analytics[self.default_config_id] = ScoringAnalytics()
            
        except Exception as e:
            logger.error(f"Error initializing default configuration: {e}")
    
    async def _process_scores(
        self,
        raw_scores: Dict[str, float],
        configuration: ScoringConfiguration
    ) -> Dict[str, float]:
        """Process and normalize raw scores"""
        try:
            processed_scores = raw_scores.copy()
            
            if configuration.normalization_enabled:
                # Normalize scores to 0-100 range
                for key, value in processed_scores.items():
                    if isinstance(value, (int, float)):
                        normalized = max(0.0, min(100.0, value))
                        processed_scores[key] = normalized
            
            # Apply scaling factor
            if configuration.score_scaling_factor != 1.0:
                for key, value in processed_scores.items():
                    if isinstance(value, (int, float)) and key != 'confidence':
                        processed_scores[key] = value * configuration.score_scaling_factor
            
            # Calculate normalized final score
            final_score = processed_scores.get('final_score', 0.0)
            processed_scores['normalized_score'] = max(0.0, min(100.0, final_score))
            
            return processed_scores
            
        except Exception as e:
            logger.error(f"Error processing scores: {e}")
            return raw_scores
    
    async def _calculate_category_scores(
        self,
        processed_scores: Dict[str, float],
        configuration: ScoringConfiguration
    ) -> Dict[ScoreCategory, float]:
        """Calculate category-based scores"""
        category_scores = {}
        category_totals = {}
        category_weights = {}
        
        try:
            # Group scores by category
            for criterion in configuration.criteria:
                category = criterion.category
                criterion_score = processed_scores.get(criterion.criterion_id, 0.0)
                
                if category not in category_totals:
                    category_totals[category] = 0.0
                    category_weights[category] = 0.0
                
                category_totals[category] += criterion_score * criterion.weight
                category_weights[category] += criterion.weight
            
            # Calculate weighted averages
            for category in category_totals:
                if category_weights[category] > 0:
                    category_scores[category] = category_totals[category] / category_weights[category]
                else:
                    category_scores[category] = 0.0
            
            return category_scores
            
        except Exception as e:
            logger.error(f"Error calculating category scores: {e}")
            return {}
    
    async def _calculate_business_metrics(
        self,
        submission_data: Dict[str, Any],
        processed_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate business impact metrics"""
        try:
            business_value = processed_scores.get('business_value_score', 0.0)
            if business_value == 0.0:
                business_value = processed_scores.get('business_impact', 0.0)
            
            # Calculate monetization potential
            monetization_potential = 0.0
            monetization_data = submission_data.get('monetization_data', {})
            
            if monetization_data.get('sponsorship_ready'):
                monetization_potential += 30.0
            if monetization_data.get('product_placement_suitable'):
                monetization_potential += 25.0
            if monetization_data.get('subscription_worthy'):
                monetization_potential += 25.0
            if monetization_data.get('premium_content'):
                monetization_potential += 20.0
            
            # Calculate collaboration compatibility
            collaboration_compatibility = processed_scores.get('collaboration_value', 0.0)
            if collaboration_compatibility == 0.0:
                collaboration_data = submission_data.get('collaboration_data', {})
                match_scores = collaboration_data.get('potential_matches', [])
                if match_scores:
                    collaboration_compatibility = sum(match_scores) / len(match_scores)
            
            return {
                'business_value': business_value,
                'monetization_potential': monetization_potential,
                'collaboration_compatibility': collaboration_compatibility
            }
            
        except Exception as e:
            logger.error(f"Error calculating business metrics: {e}")
            return {
                'business_value': 0.0,
                'monetization_potential': 0.0,
                'collaboration_compatibility': 0.0
            }
    
    async def _generate_score_analysis(
        self,
        processed_scores: Dict[str, float],
        category_scores: Dict[ScoreCategory, float],
        configuration: ScoringConfiguration
    ) -> Dict[str, List[str]]:
        """Generate score analysis and recommendations"""
        try:
            strengths = []
            improvement_areas = []
            recommendations = []
            
            # Analyze category performance
            for category, score in category_scores.items():
                if score >= 85.0:
                    strengths.append(f"Excellent {category.value.replace('_', ' ')}")
                elif score >= 70.0:
                    strengths.append(f"Good {category.value.replace('_', ' ')}")
                elif score < 50.0:
                    improvement_areas.append(f"Needs improvement in {category.value.replace('_', ' ')}")
            
            # Generate recommendations based on weaknesses
            for category, score in category_scores.items():
                if score < 60.0:
                    if category == ScoreCategory.CONTENT_QUALITY:
                        recommendations.append("Focus on improving content quality and production value")
                    elif category == ScoreCategory.CREATIVITY:
                        recommendations.append("Explore more creative and original approaches")
                    elif category == ScoreCategory.TECHNICAL_EXECUTION:
                        recommendations.append("Enhance technical skills and production techniques")
                    elif category == ScoreCategory.BUSINESS_IMPACT:
                        recommendations.append("Consider monetization and business growth opportunities")
                    elif category == ScoreCategory.AUDIENCE_ENGAGEMENT:
                        recommendations.append("Develop strategies to increase audience engagement")
            
            # Overall performance recommendations
            final_score = processed_scores.get('final_score', 0.0)
            if final_score >= 90.0:
                recommendations.append("Excellent work! Consider mentoring others or taking on advanced challenges")
            elif final_score >= 75.0:
                recommendations.append("Great performance! Focus on consistency and exploring new challenges")
            elif final_score >= 60.0:
                recommendations.append("Good foundation! Work on identified improvement areas")
            else:
                recommendations.append("Focus on fundamental skills development and seek mentorship")
            
            return {
                'strengths': strengths,
                'improvement_areas': improvement_areas,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error generating score analysis: {e}")
            return {
                'strengths': [],
                'improvement_areas': [],
                'recommendations': []
            }
    
    async def _store_score_result(self, result: ScoreResult) -> None:
        """Store score result and update percentile rank"""
        try:
            config_id = result.scorer_id
            
            if config_id not in self._score_history:
                self._score_history[config_id] = []
            
            # Calculate percentile rank
            all_scores = [r.final_score for r in self._score_history[config_id]]
            all_scores.append(result.final_score)
            all_scores.sort()
            
            rank_position = all_scores.index(result.final_score)
            result.percentile_rank = (rank_position / len(all_scores)) * 100
            
            # Store result
            self._score_history[config_id].append(result)
            
            # Limit history size
            max_history = self.config.get('max_history_size', 10000)
            if len(self._score_history[config_id]) > max_history:
                self._score_history[config_id] = self._score_history[config_id][-max_history:]
            
        except Exception as e:
            logger.error(f"Error storing score result: {e}")
    
    async def _update_analytics(self, config_id: str, result: ScoreResult) -> None:
        """Update scoring analytics"""
        try:
            if config_id not in self._analytics:
                self._analytics[config_id] = ScoringAnalytics()
            
            analytics = self._analytics[config_id]
            analytics.total_submissions_scored += 1
            
            # Update average score (running average)
            current_avg = analytics.average_score
            new_count = analytics.total_submissions_scored
            analytics.average_score = (current_avg * (new_count - 1) + result.final_score) / new_count
            
            # Update score distribution
            score_range = f"{int(result.final_score // 10) * 10}-{int(result.final_score // 10) * 10 + 9}"
            if score_range not in analytics.score_distribution:
                analytics.score_distribution[score_range] = 0
            analytics.score_distribution[score_range] += 1
            
            # Update category performance
            for category, score in result.category_scores.items():
                if category not in analytics.category_performance:
                    analytics.category_performance[category] = {
                        'total_submissions': 0,
                        'average_score': 0.0,
                        'best_score': 0.0
                    }
                
                cat_stats = analytics.category_performance[category]
                cat_stats['total_submissions'] += 1
                
                # Update category average
                current_cat_avg = cat_stats['average_score']
                cat_count = cat_stats['total_submissions']
                cat_stats['average_score'] = (current_cat_avg * (cat_count - 1) + score) / cat_count
                
                # Update best score
                cat_stats['best_score'] = max(cat_stats['best_score'], score)
            
            # Update timing metrics
            if 'average_time_ms' not in analytics.scoring_time_metrics:
                analytics.scoring_time_metrics['average_time_ms'] = 0.0
            
            current_avg_time = analytics.scoring_time_metrics['average_time_ms']
            analytics.scoring_time_metrics['average_time_ms'] = (
                (current_avg_time * (new_count - 1) + result.scoring_duration_ms) / new_count
            )
            
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")
    
    async def _validate_scoring_configuration(
        self,
        config: ScoringConfiguration
    ) -> Dict[str, Any]:
        """Validate scoring configuration"""
        errors = []
        
        try:
            # Basic validation
            if not config.name:
                errors.append("Configuration name is required")
            
            if not config.criteria:
                errors.append("At least one scoring criterion is required")
            
            # Validate weights sum to reasonable total
            total_weight = sum(criterion.weight for criterion in config.criteria)
            if total_weight == 0:
                errors.append("Total weight cannot be zero")
            
            # Validate scoring method
            if config.scoring_method not in self._algorithms:
                errors.append(f"Scoring method {config.scoring_method} not supported")
            
            # Validate criteria
            for criterion in config.criteria:
                if criterion.weight < 0:
                    errors.append(f"Criterion {criterion.name} has negative weight")
                if criterion.max_score <= criterion.min_score:
                    errors.append(f"Criterion {criterion.name} has invalid score range")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"]
            }
    
    async def _calculate_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate score distribution by ranges"""
        distribution = {}
        
        for score in scores:
            range_key = f"{int(score // 10) * 10}-{int(score // 10) * 10 + 9}"
            distribution[range_key] = distribution.get(range_key, 0) + 1
        
        return distribution
    
    async def _analyze_category_performance(
        self,
        score_history: List[ScoreResult]
    ) -> Dict[str, Dict[str, float]]:
        """Analyze performance by category"""
        category_analysis = {}
        
        for result in score_history:
            for category, score in result.category_scores.items():
                if category not in category_analysis:
                    category_analysis[category] = []
                category_analysis[category].append(score)
        
        # Calculate statistics for each category
        for category, scores in category_analysis.items():
            if scores:
                category_analysis[category] = {
                    'average': statistics.mean(scores),
                    'median': statistics.median(scores),
                    'std_dev': statistics.stdev(scores) if len(scores) > 1 else 0.0,
                    'min': min(scores),
                    'max': max(scores),
                    'count': len(scores)
                }
        
        return category_analysis
    
    async def _analyze_scoring_trends(
        self,
        score_history: List[ScoreResult]
    ) -> Dict[str, Any]:
        """Analyze scoring trends over time"""
        if len(score_history) < 2:
            return {'message': 'Insufficient data for trend analysis'}
        
        # Sort by timestamp
        sorted_history = sorted(score_history, key=lambda x: x.scoring_timestamp)
        
        # Calculate trend
        scores = [result.final_score for result in sorted_history]
        
        # Simple linear trend
        n = len(scores)
        x_values = list(range(n))
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(scores)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, scores))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator != 0:
            slope = numerator / denominator
            trend = "improving" if slope > 0.1 else "declining" if slope < -0.1 else "stable"
        else:
            slope = 0
            trend = "stable"
        
        return {
            'trend_direction': trend,
            'trend_slope': slope,
            'recent_average': statistics.mean(scores[-5:]) if len(scores) >= 5 else statistics.mean(scores),
            'overall_average': statistics.mean(scores)
        }
    
    async def _analyze_business_impact(
        self,
        score_history: List[ScoreResult]
    ) -> Dict[str, float]:
        """Analyze business impact metrics"""
        if not score_history:
            return {}
        
        business_values = [result.business_value_score for result in score_history]
        monetization_potentials = [result.monetization_potential for result in score_history]
        collaboration_scores = [result.collaboration_compatibility for result in score_history]
        
        return {
            'average_business_value': statistics.mean(business_values) if business_values else 0.0,
            'average_monetization_potential': statistics.mean(monetization_potentials) if monetization_potentials else 0.0,
            'average_collaboration_compatibility': statistics.mean(collaboration_scores) if collaboration_scores else 0.0,
            'high_business_value_rate': sum(1 for v in business_values if v >= 80) / len(business_values) if business_values else 0.0
        }