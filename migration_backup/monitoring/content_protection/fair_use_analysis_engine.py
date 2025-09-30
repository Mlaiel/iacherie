"""
Ainflue Platform - Fair Use Analysis Engine
==========================================

Enterprise-grade fair use analysis engine for automated evaluation
of copyright claims and fair use defenses in content disputes.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import asyncio
from prometheus_client import Counter, Histogram, Gauge
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

# Metrics
fair_use_analyses_total = Counter('ainflue_fair_use_analyses_total',
                                'Total fair use analyses performed', ['result', 'content_type'])
fair_use_analysis_duration = Histogram('ainflue_fair_use_analysis_duration_seconds',
                                      'Time spent analyzing fair use claims')
fair_use_confidence_score = Gauge('ainflue_fair_use_confidence_score',
                                 'Fair use analysis confidence score', ['content_id'])

class FairUseFactor(Enum):
    """The four factors of fair use analysis."""
    PURPOSE_AND_CHARACTER = "purpose_and_character"
    NATURE_OF_WORK = "nature_of_work"
    AMOUNT_USED = "amount_used"
    MARKET_EFFECT = "market_effect"

class UseType(Enum):
    """Types of content use."""
    COMMENTARY = "commentary"
    CRITICISM = "criticism"
    PARODY = "parody"
    EDUCATION = "education"
    NEWS_REPORTING = "news_reporting"
    RESEARCH = "research"
    REVIEW = "review"
    TRANSFORMATIVE = "transformative"
    COMMERCIAL = "commercial"
    NON_COMMERCIAL = "non_commercial"

class WorkType(Enum):
    """Types of original works."""
    CREATIVE_FICTION = "creative_fiction"
    FACTUAL_WORK = "factual_work"
    PUBLISHED_WORK = "published_work"
    UNPUBLISHED_WORK = "unpublished_work"
    HIGHLY_CREATIVE = "highly_creative"
    FACTUAL_COMPILATION = "factual_compilation"

class FairUseResult(Enum):
    """Fair use analysis results."""
    LIKELY_FAIR_USE = "likely_fair_use"
    POSSIBLE_FAIR_USE = "possible_fair_use"
    UNLIKELY_FAIR_USE = "unlikely_fair_use"
    NOT_FAIR_USE = "not_fair_use"
    INSUFFICIENT_DATA = "insufficient_data"

@dataclass
class ContentUseContext:
    """Context of content use for fair use analysis."""
    content_id: str
    original_work_id: str
    use_type: UseType
    work_type: WorkType
    commercial_use: bool
    transformative_purpose: bool
    educational_context: bool
    amount_used_percentage: float
    duration_used_seconds: Optional[float]
    total_duration_seconds: Optional[float]
    market_substitute: bool
    attribution_provided: bool
    user_demographics: Dict[str, Any]
    platform_context: str

@dataclass
class FactorAnalysis:
    """Analysis result for individual fair use factor."""
    factor: FairUseFactor
    score: float  # -1.0 to 1.0 (negative favors copyright holder, positive favors fair use)
    confidence: float  # 0.0 to 1.0
    reasoning: List[str]
    evidence: List[str]
    weight: float  # Factor weight in overall analysis

@dataclass
class FairUseAnalysisResult:
    """Complete fair use analysis result."""
    content_id: str
    analysis_id: str
    result: FairUseResult
    overall_score: float
    confidence_score: float
    factor_analyses: Dict[FairUseFactor, FactorAnalysis]
    context: ContentUseContext
    recommendations: List[str]
    legal_precedents: List[str]
    analysis_timestamp: datetime
    processing_time: float
    requires_human_review: bool

class FairUseAnalysisEngine:
    """Enterprise fair use analysis engine."""
    
    def __init__(self):
        self.analysis_cache = {}
        self.legal_precedents_db = {}
        self.factor_weights = {
            FairUseFactor.PURPOSE_AND_CHARACTER: 0.35,
            FairUseFactor.NATURE_OF_WORK: 0.15,
            FairUseFactor.AMOUNT_USED: 0.25,
            FairUseFactor.MARKET_EFFECT: 0.25
        }
        self.use_type_scores = {}
        self.work_type_scores = {}
        
        # Initialize scoring models
        self._initialize_scoring_models()
    
    def _initialize_scoring_models(self):
        """Initialize fair use scoring models."""
        
        # Use type scores (higher = more likely fair use)
        self.use_type_scores = {
            UseType.COMMENTARY: 0.8,
            UseType.CRITICISM: 0.8,
            UseType.PARODY: 0.9,
            UseType.EDUCATION: 0.7,
            UseType.NEWS_REPORTING: 0.8,
            UseType.RESEARCH: 0.7,
            UseType.REVIEW: 0.7,
            UseType.TRANSFORMATIVE: 0.9,
            UseType.COMMERCIAL: -0.5,
            UseType.NON_COMMERCIAL: 0.5
        }
        
        # Work type scores (higher = more protection for original work)
        self.work_type_scores = {
            WorkType.CREATIVE_FICTION: -0.6,
            WorkType.FACTUAL_WORK: 0.3,
            WorkType.PUBLISHED_WORK: 0.2,
            WorkType.UNPUBLISHED_WORK: -0.7,
            WorkType.HIGHLY_CREATIVE: -0.8,
            WorkType.FACTUAL_COMPILATION: 0.4
        }
        
        # Load legal precedents database
        self._load_legal_precedents()
    
    def _load_legal_precedents(self):
        """Load legal precedents database."""
        
        # Simulated legal precedents database
        self.legal_precedents_db = {
            'parody': [
                "Campbell v. Acuff-Rose Music (1994) - Parody can be fair use even if commercial",
                "Leibovitz v. Paramount Pictures (1998) - Parody must comment on original work"
            ],
            'transformative': [
                "Kelly v. Arriba Soft (2003) - Thumbnail images for search engine were transformative",
                "Perfect 10 v. Amazon (2007) - Transformative use analysis for search engines"
            ],
            'education': [
                "Basic Books v. Kinko's (1991) - Course packets not fair use without permission",
                "Cambridge University Press v. Patton (2012) - Educational fair use requires analysis"
            ],
            'criticism': [
                "Salinger v. Random House (1987) - Criticism requires limited quotation",
                "Wright v. Warner Books (1991) - Biographical criticism and fair use"
            ]
        }
    
    async def analyze_fair_use(self, context: ContentUseContext) -> FairUseAnalysisResult:
        """Perform comprehensive fair use analysis."""
        start_time = time.time()
        
        try:
            # Generate analysis ID
            analysis_id = f"fu_{int(time.time())}_{hashlib.md5(context.content_id.encode()).hexdigest()[:8]}"
            
            # Analyze each fair use factor
            factor_analyses = {}
            
            for factor in FairUseFactor:
                factor_analysis = await self._analyze_factor(factor, context)
                factor_analyses[factor] = factor_analysis
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(factor_analyses)
            
            # Determine result
            result = self._determine_fair_use_result(overall_score)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(factor_analyses, context)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(factor_analyses, context, result)
            
            # Find relevant legal precedents
            legal_precedents = self._find_relevant_precedents(context)
            
            # Determine if human review is required
            requires_review = self._requires_human_review(result, confidence_score, context)
            
            # Create analysis result
            analysis_result = FairUseAnalysisResult(
                content_id=context.content_id,
                analysis_id=analysis_id,
                result=result,
                overall_score=overall_score,
                confidence_score=confidence_score,
                factor_analyses=factor_analyses,
                context=context,
                recommendations=recommendations,
                legal_precedents=legal_precedents,
                analysis_timestamp=datetime.now(),
                processing_time=time.time() - start_time,
                requires_human_review=requires_review
            )
            
            # Cache result
            self.analysis_cache[analysis_id] = analysis_result
            
            # Update metrics
            fair_use_analysis_duration.observe(analysis_result.processing_time)
            fair_use_analyses_total.labels(
                result=result.value,
                content_type=context.platform_context
            ).inc()
            fair_use_confidence_score.labels(content_id=context.content_id).set(confidence_score)
            
            logger.info(f"Fair use analysis completed: {analysis_id} - Result: {result.value} "
                       f"(Score: {overall_score:.3f}, Confidence: {confidence_score:.3f})")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Fair use analysis failed: {str(e)}")
            raise
    
    async def _analyze_factor(self, factor: FairUseFactor,
                            context: ContentUseContext) -> FactorAnalysis:
        """Analyze individual fair use factor."""
        
        if factor == FairUseFactor.PURPOSE_AND_CHARACTER:
            return await self._analyze_purpose_and_character(context)
        elif factor == FairUseFactor.NATURE_OF_WORK:
            return await self._analyze_nature_of_work(context)
        elif factor == FairUseFactor.AMOUNT_USED:
            return await self._analyze_amount_used(context)
        elif factor == FairUseFactor.MARKET_EFFECT:
            return await self._analyze_market_effect(context)
        else:
            raise ValueError(f"Unknown fair use factor: {factor}")
    
    async def _analyze_purpose_and_character(self, context: ContentUseContext) -> FactorAnalysis:
        """Analyze Factor 1: Purpose and character of the use."""
        
        score = 0.0
        confidence = 0.8
        reasoning = []
        evidence = []
        
        # Use type analysis
        use_type_score = self.use_type_scores.get(context.use_type, 0.0)
        score += use_type_score * 0.4
        reasoning.append(f"Use type ({context.use_type.value}) score: {use_type_score}")
        
        # Transformative nature
        if context.transformative_purpose:
            score += 0.3
            reasoning.append("Use is transformative - adds new expression or meaning")
            evidence.append("Content adds commentary, criticism, or new creative elements")
        else:
            score -= 0.2
            reasoning.append("Use is not transformative - merely reproduces original")
        
        # Commercial vs non-commercial
        if context.commercial_use:
            score -= 0.2
            reasoning.append("Commercial use weighs against fair use")
            evidence.append("Content is used for commercial purposes")
        else:
            score += 0.1
            reasoning.append("Non-commercial use favors fair use")
        
        # Educational context
        if context.educational_context:
            score += 0.2
            reasoning.append("Educational context favors fair use")
            evidence.append("Content is used in educational setting")
        
        # Commentary, criticism, parody special consideration
        if context.use_type in [UseType.COMMENTARY, UseType.CRITICISM, UseType.PARODY]:
            score += 0.2
            reasoning.append(f"{context.use_type.value} is favored use under fair use doctrine")
            evidence.append("First Amendment considerations favor commentary and criticism")
        
        # Attribution consideration
        if context.attribution_provided:
            score += 0.1
            reasoning.append("Attribution provided (supports good faith)")
            evidence.append("Original creator credited")
        
        # Normalize score to [-1, 1]
        score = max(-1.0, min(1.0, score))
        
        return FactorAnalysis(
            factor=FairUseFactor.PURPOSE_AND_CHARACTER,
            score=score,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence,
            weight=self.factor_weights[FairUseFactor.PURPOSE_AND_CHARACTER]
        )
    
    async def _analyze_nature_of_work(self, context: ContentUseContext) -> FactorAnalysis:
        """Analyze Factor 2: Nature of the copyrighted work."""
        
        score = 0.0
        confidence = 0.7
        reasoning = []
        evidence = []
        
        # Work type analysis
        work_type_score = self.work_type_scores.get(context.work_type, 0.0)
        score += work_type_score
        reasoning.append(f"Work type ({context.work_type.value}) score: {work_type_score}")
        
        # Published vs unpublished
        if context.work_type == WorkType.PUBLISHED_WORK:
            score += 0.2
            reasoning.append("Published work has less protection under this factor")
            evidence.append("Original work is published and publicly available")
        elif context.work_type == WorkType.UNPUBLISHED_WORK:
            score -= 0.4
            reasoning.append("Unpublished work has strong protection")
            evidence.append("Original work is unpublished, affecting first publication rights")
        
        # Creative vs factual nature
        if context.work_type in [WorkType.CREATIVE_FICTION, WorkType.HIGHLY_CREATIVE]:
            score -= 0.3
            reasoning.append("Highly creative works receive stronger protection")
            evidence.append("Original work is highly creative/fictional")
        elif context.work_type in [WorkType.FACTUAL_WORK, WorkType.FACTUAL_COMPILATION]:
            score += 0.3
            reasoning.append("Factual works receive less protection")
            evidence.append("Original work is primarily factual")
        
        # Normalize score to [-1, 1]
        score = max(-1.0, min(1.0, score))
        
        return FactorAnalysis(
            factor=FairUseFactor.NATURE_OF_WORK,
            score=score,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence,
            weight=self.factor_weights[FairUseFactor.NATURE_OF_WORK]
        )
    
    async def _analyze_amount_used(self, context: ContentUseContext) -> FactorAnalysis:
        """Analyze Factor 3: Amount and substantiality of the portion used."""
        
        score = 0.0
        confidence = 0.9
        reasoning = []
        evidence = []
        
        # Quantitative analysis
        if context.amount_used_percentage <= 0.05:  # <= 5%
            score += 0.4
            reasoning.append("Very small portion used (≤5%)")
            evidence.append(f"Only {context.amount_used_percentage:.1%} of original work used")
        elif context.amount_used_percentage <= 0.10:  # <= 10%
            score += 0.2
            reasoning.append("Small portion used (≤10%)")
            evidence.append(f"{context.amount_used_percentage:.1%} of original work used")
        elif context.amount_used_percentage <= 0.25:  # <= 25%
            score -= 0.1
            reasoning.append("Moderate portion used (≤25%)")
            evidence.append(f"{context.amount_used_percentage:.1%} of original work used")
        elif context.amount_used_percentage <= 0.50:  # <= 50%
            score -= 0.3
            reasoning.append("Large portion used (≤50%)")
            evidence.append(f"{context.amount_used_percentage:.1%} of original work used")
        else:  # > 50%
            score -= 0.6
            reasoning.append("Majority of work used (>50%)")
            evidence.append(f"{context.amount_used_percentage:.1%} of original work used")
        
        # Duration analysis for time-based media
        if context.duration_used_seconds and context.total_duration_seconds:
            duration_ratio = context.duration_used_seconds / context.total_duration_seconds
            
            if duration_ratio <= 0.05:
                score += 0.2
                reasoning.append("Brief temporal excerpt used")
            elif duration_ratio > 0.30:
                score -= 0.2
                reasoning.append("Substantial temporal portion used")
            
            evidence.append(f"Duration used: {context.duration_used_seconds}s of {context.total_duration_seconds}s")
        
        # Qualitative analysis - "heart of the work"
        # This would require more sophisticated content analysis
        # For now, assume higher percentages indicate potential "heart" usage
        if context.amount_used_percentage > 0.30:
            score -= 0.2
            reasoning.append("Large portion may include 'heart of the work'")
            evidence.append("Substantial portion used may include most distinctive elements")
        
        # Context-specific adjustments
        if context.use_type == UseType.PARODY:
            # Parody may need to take enough to conjure up the original
            if 0.10 <= context.amount_used_percentage <= 0.30:
                score += 0.1
                reasoning.append("Parody context allows for sufficient taking to evoke original")
        
        if context.use_type in [UseType.COMMENTARY, UseType.CRITICISM]:
            # Commentary/criticism may justify larger quotes
            if context.amount_used_percentage <= 0.20:
                score += 0.1
                reasoning.append("Commentary/criticism context justifies reasonable quotation")
        
        # Normalize score to [-1, 1]
        score = max(-1.0, min(1.0, score))
        
        return FactorAnalysis(
            factor=FairUseFactor.AMOUNT_USED,
            score=score,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence,
            weight=self.factor_weights[FairUseFactor.AMOUNT_USED]
        )
    
    async def _analyze_market_effect(self, context: ContentUseContext) -> FactorAnalysis:
        """Analyze Factor 4: Effect of use upon potential market or value."""
        
        score = 0.0
        confidence = 0.6  # Often hardest factor to assess
        reasoning = []
        evidence = []
        
        # Market substitution analysis
        if context.market_substitute:
            score -= 0.5
            reasoning.append("Use serves as market substitute for original")
            evidence.append("Used content could replace need to purchase/license original")
        else:
            score += 0.2
            reasoning.append("Use does not substitute for original market")
        
        # Commercial use impact
        if context.commercial_use:
            score -= 0.2
            reasoning.append("Commercial use may harm market for original")
            evidence.append("Commercial exploitation without permission")
        
        # Transformative nature impact
        if context.transformative_purpose:
            score += 0.3
            reasoning.append("Transformative use less likely to harm market")
            evidence.append("New purpose/character reduces market harm")
        
        # Platform and distribution analysis
        if context.platform_context in ['youtube', 'tiktok', 'instagram']:
            if context.commercial_use:
                score -= 0.1
                reasoning.append("Social media commercial use may impact market")
            else:
                score += 0.1
                reasoning.append("Non-commercial social media use less market impact")
        
        # Educational context impact
        if context.educational_context:
            score += 0.2
            reasoning.append("Educational use typically has minimal market impact")
            evidence.append("Educational fair use consideration")
        
        # Use type specific analysis
        if context.use_type == UseType.PARODY:
            score += 0.3
            reasoning.append("Parody unlikely to harm market for original")
            evidence.append("Parody serves different market function")
        elif context.use_type in [UseType.COMMENTARY, UseType.CRITICISM]:
            score += 0.1
            reasoning.append("Commentary/criticism may actually benefit original's market")
        elif context.use_type == UseType.REVIEW:
            score += 0.2
            reasoning.append("Reviews typically benefit rather than harm market")
        
        # User demographics consideration
        if context.user_demographics.get('audience_overlap', False):
            score -= 0.1
            reasoning.append("Significant audience overlap may increase market impact")
        
        # Attribution impact
        if context.attribution_provided:
            score += 0.1
            reasoning.append("Attribution may mitigate market harm")
            evidence.append("Credit given to original creator")
        
        # Normalize score to [-1, 1]
        score = max(-1.0, min(1.0, score))
        
        return FactorAnalysis(
            factor=FairUseFactor.MARKET_EFFECT,
            score=score,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence,
            weight=self.factor_weights[FairUseFactor.MARKET_EFFECT]
        )
    
    def _calculate_overall_score(self, factor_analyses: Dict[FairUseFactor, FactorAnalysis]) -> float:
        """Calculate overall fair use score from factor analyses."""
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for factor, analysis in factor_analyses.items():
            weight = analysis.weight
            # Adjust weight by confidence
            adjusted_weight = weight * analysis.confidence
            
            weighted_sum += analysis.score * adjusted_weight
            total_weight += adjusted_weight
        
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # Normalize to [-1, 1]
        return max(-1.0, min(1.0, overall_score))
    
    def _determine_fair_use_result(self, overall_score: float) -> FairUseResult:
        """Determine fair use result from overall score."""
        
        if overall_score >= 0.5:
            return FairUseResult.LIKELY_FAIR_USE
        elif overall_score >= 0.2:
            return FairUseResult.POSSIBLE_FAIR_USE
        elif overall_score >= -0.2:
            return FairUseResult.UNLIKELY_FAIR_USE
        else:
            return FairUseResult.NOT_FAIR_USE
    
    def _calculate_confidence_score(self, factor_analyses: Dict[FairUseFactor, FactorAnalysis],
                                  context: ContentUseContext) -> float:
        """Calculate confidence in fair use analysis."""
        
        # Base confidence from factor analysis confidence
        factor_confidences = [analysis.confidence for analysis in factor_analyses.values()]
        base_confidence = np.mean(factor_confidences)
        
        # Adjust for data completeness
        data_completeness = self._assess_data_completeness(context)
        confidence = base_confidence * data_completeness
        
        # Adjust for analysis consistency
        factor_scores = [analysis.score for analysis in factor_analyses.values()]
        if len(factor_scores) > 1:
            score_variance = np.var(factor_scores)
            # Lower variance means more consistent analysis
            consistency_bonus = max(0, 0.2 - score_variance)
            confidence += consistency_bonus
        
        # Adjust for edge cases
        overall_score = self._calculate_overall_score(factor_analyses)
        if abs(overall_score) > 0.7:  # Very clear cases
            confidence += 0.1
        elif abs(overall_score) < 0.1:  # Very close cases
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _assess_data_completeness(self, context: ContentUseContext) -> float:
        """Assess completeness of data for fair use analysis."""
        
        required_fields = [
            'use_type', 'work_type', 'commercial_use',
            'transformative_purpose', 'amount_used_percentage'
        ]
        
        optional_fields = [
            'duration_used_seconds', 'total_duration_seconds',
            'market_substitute', 'attribution_provided',
            'educational_context'
        ]
        
        # Check required fields
        required_score = 0.0
        for field in required_fields:
            if hasattr(context, field) and getattr(context, field) is not None:
                required_score += 1.0
        
        required_completeness = required_score / len(required_fields)
        
        # Check optional fields
        optional_score = 0.0
        for field in optional_fields:
            if hasattr(context, field) and getattr(context, field) is not None:
                optional_score += 1.0
        
        optional_completeness = optional_score / len(optional_fields)
        
        # Weight required fields more heavily
        overall_completeness = (required_completeness * 0.8) + (optional_completeness * 0.2)
        
        return overall_completeness
    
    async def _generate_recommendations(self, factor_analyses: Dict[FairUseFactor, FactorAnalysis],
                                      context: ContentUseContext,
                                      result: FairUseResult) -> List[str]:
        """Generate recommendations based on fair use analysis."""
        
        recommendations = []
        
        # General recommendations based on result
        if result == FairUseResult.LIKELY_FAIR_USE:
            recommendations.append("Fair use defense appears strong")
            recommendations.append("Document transformative purpose and limited use")
        elif result == FairUseResult.POSSIBLE_FAIR_USE:
            recommendations.append("Fair use defense is uncertain - consider legal consultation")
            recommendations.append("Strengthen transformative elements if possible")
        elif result == FairUseResult.UNLIKELY_FAIR_USE:
            recommendations.append("Fair use defense is weak - consider obtaining permission")
            recommendations.append("Reduce amount used or increase transformative purpose")
        else:  # NOT_FAIR_USE
            recommendations.append("Fair use defense very unlikely - obtain permission or remove content")
            recommendations.append("Consider alternative approach with more transformative use")
        
        # Factor-specific recommendations
        purpose_analysis = factor_analyses[FairUseFactor.PURPOSE_AND_CHARACTER]
        if purpose_analysis.score < 0:
            if not context.transformative_purpose:
                recommendations.append("Add more transformative elements (commentary, criticism, new purpose)")
            if context.commercial_use:
                recommendations.append("Consider non-commercial distribution to strengthen fair use claim")
        
        amount_analysis = factor_analyses[FairUseFactor.AMOUNT_USED]
        if amount_analysis.score < -0.3:
            recommendations.append("Reduce amount of original work used")
            recommendations.append("Use only what is necessary for your transformative purpose")
        
        market_analysis = factor_analyses[FairUseFactor.MARKET_EFFECT]
        if market_analysis.score < 0:
            recommendations.append("Ensure use does not substitute for original work")
            if not context.attribution_provided:
                recommendations.append("Provide attribution to original creator")
        
        # Platform-specific recommendations
        if context.platform_context in ['youtube', 'tiktok']:
            recommendations.append("Consider platform-specific fair use policies")
            recommendations.append("Be prepared for Content ID claims on commercial platforms")
        
        return recommendations
    
    def _find_relevant_precedents(self, context: ContentUseContext) -> List[str]:
        """Find relevant legal precedents for the analysis."""
        
        precedents = []
        
        # Use type based precedents
        if context.use_type == UseType.PARODY:
            precedents.extend(self.legal_precedents_db.get('parody', []))
        
        if context.transformative_purpose:
            precedents.extend(self.legal_precedents_db.get('transformative', []))
        
        if context.educational_context:
            precedents.extend(self.legal_precedents_db.get('education', []))
        
        if context.use_type in [UseType.COMMENTARY, UseType.CRITICISM]:
            precedents.extend(self.legal_precedents_db.get('criticism', []))
        
        # Remove duplicates
        precedents = list(set(precedents))
        
        return precedents[:5]  # Return top 5 most relevant
    
    def _requires_human_review(self, result: FairUseResult, confidence_score: float,
                             context: ContentUseContext) -> bool:
        """Determine if human review is required."""
        
        # Low confidence always requires review
        if confidence_score < 0.6:
            return True
        
        # Borderline cases require review
        if result in [FairUseResult.POSSIBLE_FAIR_USE, FairUseResult.UNLIKELY_FAIR_USE]:
            return True
        
        # High-value content requires review
        if context.commercial_use and context.amount_used_percentage > 0.25:
            return True
        
        # Unpublished works require review
        if context.work_type == WorkType.UNPUBLISHED_WORK:
            return True
        
        # Platform with strict policies requires review
        if context.platform_context in ['youtube'] and context.commercial_use:
            return True
        
        return False
    
    async def bulk_analyze_content(self, contexts: List[ContentUseContext]) -> List[FairUseAnalysisResult]:
        """Perform bulk fair use analysis for multiple content pieces."""
        
        results = []
        
        for context in contexts:
            try:
                result = await self.analyze_fair_use(context)
                results.append(result)
            except Exception as e:
                logger.error(f"Bulk analysis failed for {context.content_id}: {str(e)}")
        
        return results
    
    async def get_cached_analysis(self, analysis_id: str) -> Optional[FairUseAnalysisResult]:
        """Get cached fair use analysis result."""
        return self.analysis_cache.get(analysis_id)
    
    async def invalidate_analysis_cache(self, content_id: str) -> None:
        """Invalidate cached analyses for content."""
        
        to_remove = []
        for analysis_id, result in self.analysis_cache.items():
            if result.content_id == content_id:
                to_remove.append(analysis_id)
        
        for analysis_id in to_remove:
            del self.analysis_cache[analysis_id]
    
    def get_fair_use_stats(self) -> Dict[str, Any]:
        """Get fair use analysis statistics."""
        
        total_analyses = len(self.analysis_cache)
        
        # Result distribution
        result_counts = {}
        confidence_scores = []
        human_review_needed = 0
        
        for analysis in self.analysis_cache.values():
            result = analysis.result.value
            result_counts[result] = result_counts.get(result, 0) + 1
            confidence_scores.append(analysis.confidence_score)
            
            if analysis.requires_human_review:
                human_review_needed += 1
        
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        
        # Use type distribution
        use_type_counts = {}
        for analysis in self.analysis_cache.values():
            use_type = analysis.context.use_type.value
            use_type_counts[use_type] = use_type_counts.get(use_type, 0) + 1
        
        return {
            'total_analyses': total_analyses,
            'result_distribution': result_counts,
            'use_type_distribution': use_type_counts,
            'average_confidence': avg_confidence,
            'human_review_required': human_review_needed,
            'human_review_percentage': (human_review_needed / total_analyses * 100) if total_analyses > 0 else 0
        }

# Global fair use analysis engine instance
fair_use_analysis_engine = FairUseAnalysisEngine()