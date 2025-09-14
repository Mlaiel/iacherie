"""Business Quality Validator - Consolidated Business Rules & Quality Assessment
==============================================================================

Industrial-grade business rules validation and content quality assessment system
for the IA Influencer Agent Platform, combining business logic enforcement,
quality scoring, and creator workflow optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited

Consolidated Validation Capabilities:
- Business rules validation (monetization, collaboration, workflow)
- Content quality assessment with AI-powered scoring
- Creator performance analytics and optimization
- Platform-specific business logic enforcement
- Engagement prediction and optimization
- Revenue optimization recommendations
- Quality gates and automated approval workflows
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Union, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
from pathlib import Path
import statistics
import re

logger = logging.getLogger(__name__)

class BusinessRuleType(Enum):
    """Types of business rules."""
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    CONTENT_WORKFLOW = "content_workflow"
    CREATOR_REQUIREMENTS = "creator_requirements"
    PLATFORM_COMPLIANCE = "platform_compliance"
    REVENUE_OPTIMIZATION = "revenue_optimization"
    ENGAGEMENT_OPTIMIZATION = "engagement_optimization"
    BRAND_SAFETY = "brand_safety"
    AUDIENCE_TARGETING = "audience_targeting"
    PERFORMANCE_METRICS = "performance_metrics"

class RuleSeverity(Enum):
    """Business rule violation severity."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ValidationContext(Enum):
    """Context for business validation."""
    UPLOAD = "upload"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    PUBLICATION = "publication"
    PERFORMANCE_REVIEW = "performance_review"
    OPTIMIZATION = "optimization"

class QualityDimension(Enum):
    """Quality assessment dimensions."""
    TECHNICAL_QUALITY = "technical_quality"
    CONTENT_RELEVANCE = "content_relevance"
    ENGAGEMENT_POTENTIAL = "engagement_potential"
    BRAND_ALIGNMENT = "brand_alignment"
    AUDIENCE_APPEAL = "audience_appeal"
    PRODUCTION_VALUE = "production_value"
    ORIGINALITY = "originality"
    TRENDING_POTENTIAL = "trending_potential"
    MONETIZATION_POTENTIAL = "monetization_potential"
    VIRAL_POTENTIAL = "viral_potential"

class QualityMetric(Enum):
    """Specific quality metrics."""
    AUDIO_CLARITY = "audio_clarity"
    VIDEO_RESOLUTION = "video_resolution"
    COLOR_GRADING = "color_grading"
    EDITING_QUALITY = "editing_quality"
    STORYTELLING = "storytelling"
    CREATIVITY = "creativity"
    AUTHENTICITY = "authenticity"
    EDUCATIONAL_VALUE = "educational_value"
    ENTERTAINMENT_VALUE = "entertainment_value"
    COMMERCIAL_APPEAL = "commercial_appeal"

class QualityLevel(Enum):
    """Quality assessment levels."""
    POOR = "poor"
    BELOW_AVERAGE = "below_average"
    AVERAGE = "average"
    GOOD = "good"
    EXCELLENT = "excellent"
    EXCEPTIONAL = "exceptional"

@dataclass
class BusinessRule:
    """Business rule definition."""
    rule_type: BusinessRuleType
    name: str
    description: str
    severity: RuleSeverity
    conditions: Dict[str, Any]
    consequences: List[str]
    remediation_steps: List[str]
    applicable_contexts: List[ValidationContext] = field(default_factory=list)
    platform_specific: Optional[str] = None
    enabled: bool = True

@dataclass
class BusinessValidationResult:
    """Business rules validation result."""
    is_compliant: bool
    compliance_score: float
    violations: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    revenue_impact: Optional[float] = None
    engagement_impact: Optional[float] = None
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    validation_context: ValidationContext = ValidationContext.UPLOAD
    business_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QualityScore:
    """Content quality score details."""
    overall_score: float
    dimension_scores: Dict[QualityDimension, float] = field(default_factory=dict)
    metric_scores: Dict[QualityMetric, float] = field(default_factory=dict)
    quality_level: QualityLevel = QualityLevel.AVERAGE
    confidence: float = 0.0
    improvement_areas: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)

@dataclass
class QualityValidationResult:
    """Quality assessment result."""
    quality_score: QualityScore
    meets_standards: bool
    quality_gate_passed: bool
    optimization_suggestions: List[str] = field(default_factory=list)
    predicted_performance: Dict[str, float] = field(default_factory=dict)
    market_analysis: Dict[str, Any] = field(default_factory=dict)
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessment_duration_ms: int = 0
    ai_confidence: float = 0.0

class BusinessQualityValidator:
    """Consolidated business rules and quality assessment validator."""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the business quality validator.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.business_rules = self._load_business_rules()
        self.quality_standards = self._load_quality_standards()
        
        # Business validation settings
        self.min_compliance_score = self.config.get('min_compliance_score', 0.8)
        self.quality_threshold = self.config.get('quality_threshold', 0.7)
        self.ai_analysis_enabled = self.config.get('ai_analysis_enabled', True)
        self.performance_prediction_enabled = self.config.get('performance_prediction_enabled', True)
        
        logger.info("BusinessQualityValidator initialized")
    
    def _load_business_rules(self) -> List[BusinessRule]:
        """Load business rules configuration.
        
        Returns:
            List of business rules
        """
        rules = [
            # Monetization Rules
            BusinessRule(
                rule_type=BusinessRuleType.MONETIZATION,
                name="minimum_content_length",
                description="Content must meet minimum length requirements for monetization",
                severity=RuleSeverity.ERROR,
                conditions={
                    'min_video_duration': 60,  # seconds
                    'min_audio_duration': 180,  # seconds  
                    'min_text_length': 500,  # characters
                },
                consequences=["Content not eligible for monetization"],
                remediation_steps=["Extend content to meet minimum length requirements"],
                applicable_contexts=[ValidationContext.MONETIZATION, ValidationContext.UPLOAD]
            ),
            
            BusinessRule(
                rule_type=BusinessRuleType.MONETIZATION,
                name="copyright_clearance",
                description="All content must have proper copyright clearance for monetization",
                severity=RuleSeverity.CRITICAL,
                conditions={
                    'requires_clearance': True,
                    'clearance_verified': True
                },
                consequences=["Monetization disabled", "Legal liability risk"],
                remediation_steps=["Verify copyright ownership", "Obtain proper licensing"],
                applicable_contexts=[ValidationContext.MONETIZATION, ValidationContext.PUBLICATION]
            ),
            
            # Collaboration Rules
            BusinessRule(
                rule_type=BusinessRuleType.COLLABORATION,
                name="creator_verification",
                description="Creators must be verified for collaboration eligibility",
                severity=RuleSeverity.ERROR,
                conditions={
                    'verification_required': True,
                    'min_followers': 1000,
                    'account_age_days': 30
                },
                consequences=["Collaboration requests blocked"],
                remediation_steps=["Complete verification process", "Build follower base"],
                applicable_contexts=[ValidationContext.COLLABORATION]
            ),
            
            BusinessRule(
                rule_type=BusinessRuleType.COLLABORATION,
                name="content_consistency",
                description="Collaborative content must maintain consistency across creators",
                severity=RuleSeverity.WARNING,
                conditions={
                    'style_consistency_score': 0.7,
                    'brand_alignment_score': 0.8
                },
                consequences=["Reduced collaboration success rate"],
                remediation_steps=["Align content styles", "Establish brand guidelines"],
                applicable_contexts=[ValidationContext.COLLABORATION]
            ),
            
            # Content Workflow Rules
            BusinessRule(
                rule_type=BusinessRuleType.CONTENT_WORKFLOW,
                name="quality_gates",
                description="Content must pass quality gates before publication",
                severity=RuleSeverity.ERROR,
                conditions={
                    'technical_quality_score': 0.7,
                    'content_safety_score': 0.9,
                    'engagement_prediction': 0.6
                },
                consequences=["Content blocked from publication"],
                remediation_steps=["Improve technical quality", "Address safety concerns"],
                applicable_contexts=[ValidationContext.UPLOAD, ValidationContext.PUBLICATION]
            ),
            
            # Creator Requirements
            BusinessRule(
                rule_type=BusinessRuleType.CREATOR_REQUIREMENTS,
                name="performance_standards",
                description="Creators must maintain minimum performance standards",
                severity=RuleSeverity.WARNING,
                conditions={
                    'avg_engagement_rate': 0.03,
                    'content_quality_avg': 0.7,
                    'upload_consistency': 0.8
                },
                consequences=["Reduced platform visibility", "Limited monetization"],
                remediation_steps=["Improve content quality", "Maintain regular uploads"],
                applicable_contexts=[ValidationContext.PERFORMANCE_REVIEW]
            ),
            
            # Brand Safety Rules
            BusinessRule(
                rule_type=BusinessRuleType.BRAND_SAFETY,
                name="advertiser_friendly",
                description="Content must be advertiser-friendly for maximum monetization",
                severity=RuleSeverity.WARNING,
                conditions={
                    'controversial_content': False,
                    'brand_safety_score': 0.8,
                    'suitable_for_ads': True
                },
                consequences=["Limited ad revenue", "Restricted brand partnerships"],
                remediation_steps=["Avoid controversial topics", "Focus on brand-safe content"],
                applicable_contexts=[ValidationContext.MONETIZATION, ValidationContext.PUBLICATION]
            )
        ]
        
        return rules
    
    def _load_quality_standards(self) -> Dict[QualityDimension, Dict[str, Any]]:
        """Load quality assessment standards.
        
        Returns:
            Quality standards configuration
        """
        standards = {
            QualityDimension.TECHNICAL_QUALITY: {
                'weight': 0.25,
                'metrics': {
                    QualityMetric.AUDIO_CLARITY: {'weight': 0.3, 'min_score': 0.7},
                    QualityMetric.VIDEO_RESOLUTION: {'weight': 0.3, 'min_score': 0.6},
                    QualityMetric.COLOR_GRADING: {'weight': 0.2, 'min_score': 0.5},
                    QualityMetric.EDITING_QUALITY: {'weight': 0.2, 'min_score': 0.6}
                }
            },
            QualityDimension.CONTENT_RELEVANCE: {
                'weight': 0.2,
                'metrics': {
                    QualityMetric.STORYTELLING: {'weight': 0.4, 'min_score': 0.6},
                    QualityMetric.EDUCATIONAL_VALUE: {'weight': 0.3, 'min_score': 0.5},
                    QualityMetric.ENTERTAINMENT_VALUE: {'weight': 0.3, 'min_score': 0.5}
                }
            },
            QualityDimension.ENGAGEMENT_POTENTIAL: {
                'weight': 0.2,
                'metrics': {
                    QualityMetric.CREATIVITY: {'weight': 0.4, 'min_score': 0.6},
                    QualityMetric.AUTHENTICITY: {'weight': 0.3, 'min_score': 0.7},
                    QualityMetric.TRENDING_POTENTIAL: {'weight': 0.3, 'min_score': 0.5}
                }
            },
            QualityDimension.BRAND_ALIGNMENT: {
                'weight': 0.15,
                'metrics': {
                    QualityMetric.COMMERCIAL_APPEAL: {'weight': 0.6, 'min_score': 0.6},
                    QualityMetric.AUTHENTICITY: {'weight': 0.4, 'min_score': 0.7}
                }
            },
            QualityDimension.PRODUCTION_VALUE: {
                'weight': 0.2,
                'metrics': {
                    QualityMetric.EDITING_QUALITY: {'weight': 0.4, 'min_score': 0.6},
                    QualityMetric.AUDIO_CLARITY: {'weight': 0.3, 'min_score': 0.7},
                    QualityMetric.VIDEO_RESOLUTION: {'weight': 0.3, 'min_score': 0.6}
                }
            }
        }
        
        return standards
    
    async def validate_business_rules(self, content_metadata: Dict[str, Any],
                                    context: ValidationContext = ValidationContext.UPLOAD,
                                    platform: Optional[str] = None) -> BusinessValidationResult:
        """Validate content against business rules.
        
        Args:
            content_metadata: Content metadata and context information
            context: Validation context
            platform: Optional platform name for platform-specific rules
            
        Returns:
            BusinessValidationResult with compliance status
        """
        start_time = datetime.now()
        violations = []
        warnings = []
        recommendations = []
        business_metrics = {}
        
        try:
            # Filter applicable rules
            applicable_rules = [
                rule for rule in self.business_rules
                if (context in rule.applicable_contexts or not rule.applicable_contexts) and
                   rule.enabled and
                   (rule.platform_specific is None or rule.platform_specific == platform)
            ]
            
            # Validate each rule
            compliance_scores = []
            for rule in applicable_rules:
                rule_result = await self._validate_business_rule(content_metadata, rule)
                compliance_scores.append(rule_result['compliance_score'])
                
                if rule_result['violation']:
                    violation_data = {
                        'rule_name': rule.name,
                        'rule_type': rule.rule_type.value,
                        'severity': rule.severity.value,
                        'description': rule.description,
                        'violation_details': rule_result['violation_details'],
                        'consequences': rule.consequences,
                        'remediation_steps': rule.remediation_steps
                    }
                    
                    if rule.severity in [RuleSeverity.ERROR, RuleSeverity.CRITICAL]:
                        violations.append(violation_data)
                    else:
                        warnings.append(f"{rule.name}: {rule.description}")
                
                # Collect recommendations
                if rule_result['recommendations']:
                    recommendations.extend(rule_result['recommendations'])
            
            # Calculate overall compliance score
            if compliance_scores:
                compliance_score = statistics.mean(compliance_scores)
            else:
                compliance_score = 1.0
            
            # Determine if content is compliant
            is_compliant = (compliance_score >= self.min_compliance_score and 
                          not any(v['severity'] in ['error', 'critical'] for v in violations))
            
            # Calculate business impact estimates
            revenue_impact = self._estimate_revenue_impact(content_metadata, violations, warnings)
            engagement_impact = self._estimate_engagement_impact(content_metadata, violations, warnings)
            
            # Collect business metrics
            business_metrics.update({
                'total_rules_checked': len(applicable_rules),
                'rules_passed': len([s for s in compliance_scores if s >= 0.8]),
                'revenue_potential': revenue_impact,
                'engagement_potential': engagement_impact,
                'optimization_opportunities': len(recommendations)
            })
            
            return BusinessValidationResult(
                is_compliant=is_compliant,
                compliance_score=compliance_score,
                violations=violations,
                warnings=warnings,
                recommendations=recommendations,
                revenue_impact=revenue_impact,
                engagement_impact=engagement_impact,
                validated_at=start_time,
                validation_context=context,
                business_metrics=business_metrics
            )
            
        except Exception as e:
            logger.error(f"Business validation failed: {e}")
            return BusinessValidationResult(
                is_compliant=False,
                compliance_score=0.0,
                violations=[{
                    'rule_name': 'validation_error',
                    'rule_type': 'system_error',
                    'severity': 'critical',
                    'description': f"Business validation error: {str(e)}",
                    'consequences': ['Content cannot be processed'],
                    'remediation_steps': ['Contact technical support']
                }],
                validation_context=context,
                business_metrics={'validation_error': True}
            )
    
    async def assess_content_quality(self, content_data: Dict[str, Any],
                                   content_type: str = "mixed") -> QualityValidationResult:
        """Assess content quality across multiple dimensions.
        
        Args:
            content_data: Content data and metadata for assessment
            content_type: Type of content (video, audio, image, text, mixed)
            
        Returns:
            QualityValidationResult with quality assessment
        """
        start_time = datetime.now()
        
        try:
            # Assess quality across all dimensions
            dimension_scores = {}
            metric_scores = {}
            
            for dimension, standards in self.quality_standards.items():
                dimension_score = await self._assess_quality_dimension(
                    content_data, dimension, standards, content_type
                )
                dimension_scores[dimension] = dimension_score
                
                # Collect metric scores for this dimension
                for metric, metric_config in standards['metrics'].items():
                    metric_score = await self._assess_quality_metric(
                        content_data, metric, metric_config, content_type
                    )
                    metric_scores[metric] = metric_score
            
            # Calculate overall quality score (weighted)
            overall_score = sum(
                score * self.quality_standards[dim]['weight']
                for dim, score in dimension_scores.items()
            )
            
            # Determine quality level
            quality_level = self._determine_quality_level(overall_score)
            
            # Calculate AI confidence
            ai_confidence = self._calculate_ai_confidence(content_data, metric_scores)
            
            # Identify improvement areas and strengths
            improvement_areas = self._identify_improvement_areas(dimension_scores, metric_scores)
            strengths = self._identify_strengths(dimension_scores, metric_scores)
            
            # Create quality score object
            quality_score = QualityScore(
                overall_score=overall_score,
                dimension_scores=dimension_scores,
                metric_scores=metric_scores,
                quality_level=quality_level,
                confidence=ai_confidence,
                improvement_areas=improvement_areas,
                strengths=strengths
            )
            
            # Determine if quality standards are met
            meets_standards = overall_score >= self.quality_threshold
            quality_gate_passed = (meets_standards and 
                                 all(score >= 0.6 for score in dimension_scores.values()))
            
            # Generate optimization suggestions
            optimization_suggestions = self._generate_optimization_suggestions(
                quality_score, content_data, content_type
            )
            
            # Predict performance if enabled
            predicted_performance = {}
            market_analysis = {}
            
            if self.performance_prediction_enabled:
                predicted_performance = await self._predict_content_performance(
                    content_data, quality_score, content_type
                )
                market_analysis = await self._analyze_market_potential(
                    content_data, quality_score, content_type
                )
            
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return QualityValidationResult(
                quality_score=quality_score,
                meets_standards=meets_standards,
                quality_gate_passed=quality_gate_passed,
                optimization_suggestions=optimization_suggestions,
                predicted_performance=predicted_performance,
                market_analysis=market_analysis,
                assessed_at=start_time,
                assessment_duration_ms=duration_ms,
                ai_confidence=ai_confidence
            )
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return QualityValidationResult(
                quality_score=QualityScore(
                    overall_score=0.0,
                    quality_level=QualityLevel.POOR,
                    improvement_areas=["Quality assessment failed - manual review required"]
                ),
                meets_standards=False,
                quality_gate_passed=False,
                optimization_suggestions=["Contact technical support for quality assessment"],
                assessed_at=start_time,
                assessment_duration_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )
    
    async def _validate_business_rule(self, metadata: Dict[str, Any], 
                                    rule: BusinessRule) -> Dict[str, Any]:
        """Validate a specific business rule.
        
        Args:
            metadata: Content metadata
            rule: Business rule to validate
            
        Returns:
            Rule validation result
        """
        compliance_score = 1.0
        violation = False
        violation_details = []
        recommendations = []
        
        # Check each condition in the rule
        for condition_key, expected_value in rule.conditions.items():
            actual_value = metadata.get(condition_key)
            
            if actual_value is None:
                violation = True
                compliance_score *= 0.5
                violation_details.append(f"Missing required field: {condition_key}")
                recommendations.append(f"Provide {condition_key} in content metadata")
                continue
            
            # Type-specific validation
            if isinstance(expected_value, bool):
                if actual_value != expected_value:
                    violation = True
                    compliance_score *= 0.7
                    violation_details.append(f"{condition_key}: expected {expected_value}, got {actual_value}")
            
            elif isinstance(expected_value, (int, float)):
                if actual_value < expected_value:
                    violation = True
                    compliance_score *= (actual_value / expected_value) if actual_value > 0 else 0.1
                    violation_details.append(f"{condition_key}: below minimum {expected_value}, got {actual_value}")
                    recommendations.append(f"Increase {condition_key} to at least {expected_value}")
            
            elif isinstance(expected_value, str):
                if actual_value != expected_value:
                    violation = True
                    compliance_score *= 0.8
                    violation_details.append(f"{condition_key}: expected '{expected_value}', got '{actual_value}'")
        
        return {
            'compliance_score': compliance_score,
            'violation': violation,
            'violation_details': violation_details,
            'recommendations': recommendations
        }
    
    async def _assess_quality_dimension(self, content_data: Dict[str, Any],
                                      dimension: QualityDimension,
                                      standards: Dict[str, Any],
                                      content_type: str) -> float:
        """Assess quality for a specific dimension.
        
        Args:
            content_data: Content data
            dimension: Quality dimension to assess
            standards: Quality standards for this dimension
            content_type: Type of content
            
        Returns:
            Quality score for the dimension (0.0 to 1.0)
        """
        metric_scores = []
        
        for metric, metric_config in standards['metrics'].items():
            metric_score = await self._assess_quality_metric(
                content_data, metric, metric_config, content_type
            )
            weighted_score = metric_score * metric_config['weight']
            metric_scores.append(weighted_score)
        
        if metric_scores:
            return sum(metric_scores)
        else:
            return 0.5  # Default score if no metrics available
    
    async def _assess_quality_metric(self, content_data: Dict[str, Any],
                                   metric: QualityMetric,
                                   metric_config: Dict[str, Any],
                                   content_type: str) -> float:
        """Assess a specific quality metric.
        
        Args:
            content_data: Content data
            metric: Quality metric to assess
            metric_config: Metric configuration
            content_type: Type of content
            
        Returns:
            Quality score for the metric (0.0 to 1.0)
        """
        # Simplified metric assessment - in production, this would use AI models
        score = 0.5  # Default score
        
        try:
            if metric == QualityMetric.AUDIO_CLARITY:
                # Assess audio clarity based on bitrate, noise levels, etc.
                bitrate = content_data.get('audio_bitrate', 128)
                noise_level = content_data.get('noise_level', 0.5)
                score = min(1.0, (bitrate / 320) * (1 - noise_level))
            
            elif metric == QualityMetric.VIDEO_RESOLUTION:
                # Assess video resolution quality
                resolution = content_data.get('video_resolution', '720p')
                resolution_scores = {'480p': 0.5, '720p': 0.7, '1080p': 0.9, '4K': 1.0}
                score = resolution_scores.get(resolution, 0.5)
            
            elif metric == QualityMetric.STORYTELLING:
                # Assess storytelling quality (simplified)
                has_intro = content_data.get('has_intro', False)
                has_conclusion = content_data.get('has_conclusion', False)
                narrative_flow = content_data.get('narrative_flow_score', 0.5)
                score = (has_intro * 0.3 + has_conclusion * 0.3 + narrative_flow * 0.4)
            
            elif metric == QualityMetric.CREATIVITY:
                # Assess creativity based on originality and uniqueness
                originality_score = content_data.get('originality_score', 0.5)
                uniqueness_score = content_data.get('uniqueness_score', 0.5)
                score = (originality_score + uniqueness_score) / 2
            
            elif metric == QualityMetric.AUTHENTICITY:
                # Assess authenticity based on creator consistency
                brand_consistency = content_data.get('brand_consistency', 0.5)
                voice_consistency = content_data.get('voice_consistency', 0.5)
                score = (brand_consistency + voice_consistency) / 2
            
            # Apply AI enhancement if enabled
            if self.ai_analysis_enabled and 'ai_quality_scores' in content_data:
                ai_score = content_data['ai_quality_scores'].get(metric.value, score)
                # Blend traditional and AI scores
                score = (score * 0.3 + ai_score * 0.7)
            
            # Ensure score is within bounds
            score = max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.warning(f"Failed to assess metric {metric.value}: {e}")
            score = 0.5  # Fallback score
        
        return score
    
    def _determine_quality_level(self, overall_score: float) -> QualityLevel:
        """Determine quality level based on overall score.
        
        Args:
            overall_score: Overall quality score (0.0 to 1.0)
            
        Returns:
            Quality level
        """
        if overall_score >= 0.95:
            return QualityLevel.EXCEPTIONAL
        elif overall_score >= 0.85:
            return QualityLevel.EXCELLENT
        elif overall_score >= 0.75:
            return QualityLevel.GOOD
        elif overall_score >= 0.6:
            return QualityLevel.AVERAGE
        elif overall_score >= 0.4:
            return QualityLevel.BELOW_AVERAGE
        else:
            return QualityLevel.POOR
    
    def _calculate_ai_confidence(self, content_data: Dict[str, Any], 
                               metric_scores: Dict[QualityMetric, float]) -> float:
        """Calculate AI confidence in quality assessment.
        
        Args:
            content_data: Content data
            metric_scores: Metric scores
            
        Returns:
            AI confidence score (0.0 to 1.0)
        """
        confidence_factors = []
        
        # Data availability factor
        data_completeness = len([k for k in content_data.keys() if content_data[k] is not None]) / 10
        confidence_factors.append(min(1.0, data_completeness))
        
        # AI model availability factor
        if 'ai_quality_scores' in content_data:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.5)
        
        # Score consistency factor
        if len(metric_scores) > 1:
            score_variance = statistics.variance(metric_scores.values())
            consistency = max(0.0, 1.0 - score_variance)
            confidence_factors.append(consistency)
        
        return statistics.mean(confidence_factors) if confidence_factors else 0.5
    
    def _identify_improvement_areas(self, dimension_scores: Dict[QualityDimension, float],
                                  metric_scores: Dict[QualityMetric, float]) -> List[str]:
        """Identify areas for quality improvement.
        
        Args:
            dimension_scores: Scores by dimension
            metric_scores: Scores by metric
            
        Returns:
            List of improvement recommendations
        """
        improvements = []
        
        # Check dimension scores
        for dimension, score in dimension_scores.items():
            if score < 0.6:
                improvements.append(f"Improve {dimension.value.replace('_', ' ')}")
        
        # Check critical metrics
        critical_metrics = [
            QualityMetric.AUDIO_CLARITY,
            QualityMetric.VIDEO_RESOLUTION,
            QualityMetric.STORYTELLING
        ]
        
        for metric in critical_metrics:
            if metric in metric_scores and metric_scores[metric] < 0.6:
                improvements.append(f"Enhance {metric.value.replace('_', ' ')}")
        
        return improvements[:5]  # Limit to top 5 improvements
    
    def _identify_strengths(self, dimension_scores: Dict[QualityDimension, float],
                          metric_scores: Dict[QualityMetric, float]) -> List[str]:
        """Identify content strengths.
        
        Args:
            dimension_scores: Scores by dimension
            metric_scores: Scores by metric
            
        Returns:
            List of content strengths
        """
        strengths = []
        
        # Check dimension strengths
        for dimension, score in dimension_scores.items():
            if score >= 0.8:
                strengths.append(f"Excellent {dimension.value.replace('_', ' ')}")
        
        # Check metric strengths
        for metric, score in metric_scores.items():
            if score >= 0.85:
                strengths.append(f"High-quality {metric.value.replace('_', ' ')}")
        
        return strengths[:3]  # Limit to top 3 strengths
    
    def _generate_optimization_suggestions(self, quality_score: QualityScore,
                                         content_data: Dict[str, Any],
                                         content_type: str) -> List[str]:
        """Generate optimization suggestions based on quality assessment.
        
        Args:
            quality_score: Quality assessment results
            content_data: Content data
            content_type: Type of content
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        # Technical optimization suggestions
        if QualityDimension.TECHNICAL_QUALITY in quality_score.dimension_scores:
            tech_score = quality_score.dimension_scores[QualityDimension.TECHNICAL_QUALITY]
            if tech_score < 0.7:
                suggestions.append("Consider upgrading recording equipment for better technical quality")
                suggestions.append("Use professional editing software for post-production enhancement")
        
        # Content optimization suggestions
        if quality_score.overall_score < 0.8:
            suggestions.append("Focus on stronger storytelling elements")
            suggestions.append("Increase audience engagement through interactive elements")
        
        # Platform-specific suggestions
        if content_type == "video":
            suggestions.append("Optimize thumbnail design for higher click-through rates")
            suggestions.append("Add closed captions for accessibility and SEO")
        elif content_type == "audio":
            suggestions.append("Create eye-catching cover art")
            suggestions.append("Optimize audio levels for consistent listening experience")
        
        # Engagement optimization
        if QualityDimension.ENGAGEMENT_POTENTIAL in quality_score.dimension_scores:
            engagement_score = quality_score.dimension_scores[QualityDimension.ENGAGEMENT_POTENTIAL]
            if engagement_score < 0.7:
                suggestions.append("Include call-to-action elements to boost engagement")
                suggestions.append("Use trending topics or hashtags relevant to your niche")
        
        return suggestions[:6]  # Limit to top 6 suggestions
    
    async def _predict_content_performance(self, content_data: Dict[str, Any],
                                         quality_score: QualityScore,
                                         content_type: str) -> Dict[str, float]:
        """Predict content performance based on quality and metadata.
        
        Args:
            content_data: Content data
            quality_score: Quality assessment
            content_type: Type of content
            
        Returns:
            Performance predictions
        """
        # Simplified performance prediction model
        base_performance = quality_score.overall_score
        
        # Adjust based on content characteristics
        trending_factor = content_data.get('trending_score', 0.5)
        timing_factor = content_data.get('optimal_timing_score', 0.7)
        audience_match = content_data.get('audience_match_score', 0.6)
        
        # Calculate performance metrics
        predicted_engagement = base_performance * 0.5 + trending_factor * 0.3 + audience_match * 0.2
        predicted_reach = base_performance * 0.4 + timing_factor * 0.3 + trending_factor * 0.3
        predicted_retention = quality_score.dimension_scores.get(QualityDimension.CONTENT_RELEVANCE, 0.5)
        viral_potential = (quality_score.dimension_scores.get(QualityDimension.ENGAGEMENT_POTENTIAL, 0.5) * 
                         trending_factor)
        
        return {
            'engagement_rate': min(1.0, predicted_engagement),
            'reach_potential': min(1.0, predicted_reach),
            'retention_rate': min(1.0, predicted_retention),
            'viral_potential': min(1.0, viral_potential),
            'monetization_potential': quality_score.dimension_scores.get(QualityDimension.BRAND_ALIGNMENT, 0.5)
        }
    
    async def _analyze_market_potential(self, content_data: Dict[str, Any],
                                      quality_score: QualityScore,
                                      content_type: str) -> Dict[str, Any]:
        """Analyze market potential for content.
        
        Args:
            content_data: Content data
            quality_score: Quality assessment
            content_type: Type of content
            
        Returns:
            Market analysis data
        """
        return {
            'market_saturation': content_data.get('niche_saturation', 0.5),
            'competition_level': content_data.get('competition_score', 0.6),
            'audience_size': content_data.get('target_audience_size', 'medium'),
            'growth_potential': quality_score.overall_score * 0.8,
            'recommended_platforms': self._recommend_platforms(content_data, quality_score, content_type),
            'optimal_timing': content_data.get('optimal_posting_time', 'peak_hours'),
            'target_demographics': content_data.get('target_demographics', ['18-34', 'mixed_gender'])
        }
    
    def _recommend_platforms(self, content_data: Dict[str, Any],
                           quality_score: QualityScore,
                           content_type: str) -> List[str]:
        """Recommend optimal platforms for content.
        
        Args:
            content_data: Content data
            quality_score: Quality assessment
            content_type: Type of content
            
        Returns:
            List of recommended platforms
        """
        recommendations = []
        
        # Platform suitability based on content type and quality
        if content_type == "video":
            if quality_score.overall_score >= 0.8:
                recommendations.extend(["YouTube", "TikTok", "Instagram"])
            else:
                recommendations.extend(["TikTok", "Instagram"])
        
        elif content_type == "audio":
            recommendations.extend(["Spotify", "Apple Podcasts", "YouTube"])
        
        elif content_type == "image":
            recommendations.extend(["Instagram", "Pinterest", "Twitter"])
        
        # Adjust based on engagement potential
        engagement_score = quality_score.dimension_scores.get(QualityDimension.ENGAGEMENT_POTENTIAL, 0.5)
        if engagement_score >= 0.8:
            if "TikTok" not in recommendations:
                recommendations.append("TikTok")
        
        return recommendations[:3]  # Limit to top 3 platforms
    
    def _estimate_revenue_impact(self, metadata: Dict[str, Any], 
                               violations: List[Dict[str, Any]],
                               warnings: List[str]) -> float:
        """Estimate revenue impact of business rule compliance.
        
        Args:
            metadata: Content metadata
            violations: Business rule violations
            warnings: Business rule warnings
            
        Returns:
            Estimated revenue impact multiplier (0.0 to 1.0)
        """
        base_revenue_potential = 1.0
        
        # Reduce based on violations
        for violation in violations:
            if violation['severity'] == 'critical':
                base_revenue_potential *= 0.1  # Critical issues severely impact revenue
            elif violation['severity'] == 'error':
                base_revenue_potential *= 0.5  # Errors significantly reduce revenue
            elif violation['severity'] == 'warning':
                base_revenue_potential *= 0.8  # Warnings moderately affect revenue
        
        # Account for content quality factors
        content_quality = metadata.get('content_quality_score', 0.7)
        brand_safety = metadata.get('brand_safety_score', 0.8)
        
        revenue_multiplier = base_revenue_potential * content_quality * brand_safety
        
        return max(0.0, min(1.0, revenue_multiplier))
    
    def _estimate_engagement_impact(self, metadata: Dict[str, Any],
                                  violations: List[Dict[str, Any]],
                                  warnings: List[str]) -> float:
        """Estimate engagement impact of business rule compliance.
        
        Args:
            metadata: Content metadata
            violations: Business rule violations
            warnings: Business rule warnings
            
        Returns:
            Estimated engagement impact multiplier (0.0 to 1.0)
        """
        base_engagement_potential = 1.0
        
        # Reduce based on violations (less severe impact than revenue)
        for violation in violations:
            if violation['severity'] == 'critical':
                base_engagement_potential *= 0.3
            elif violation['severity'] == 'error':
                base_engagement_potential *= 0.7
            elif violation['severity'] == 'warning':
                base_engagement_potential *= 0.9
        
        # Account for engagement-specific factors
        engagement_quality = metadata.get('engagement_prediction', 0.6)
        audience_match = metadata.get('audience_match_score', 0.7)
        
        engagement_multiplier = base_engagement_potential * engagement_quality * audience_match
        
        return max(0.0, min(1.0, engagement_multiplier))

# Convenience functions for direct validation
async def validate_business_rules(content_metadata: Dict[str, Any],
                                context: ValidationContext = ValidationContext.UPLOAD,
                                platform: Optional[str] = None,
                                config: Optional[Dict[str, Any]] = None) -> BusinessValidationResult:
    """Validate business rules (convenience function).
    
    Args:
        content_metadata: Content metadata
        context: Validation context
        platform: Platform name
        config: Optional validator configuration
        
    Returns:
        BusinessValidationResult
    """
    validator = BusinessQualityValidator(config)
    return await validator.validate_business_rules(content_metadata, context, platform)

async def assess_content_quality(content_data: Dict[str, Any],
                               content_type: str = "mixed",
                               config: Optional[Dict[str, Any]] = None) -> QualityValidationResult:
    """Assess content quality (convenience function).
    
    Args:
        content_data: Content data
        content_type: Type of content
        config: Optional validator configuration
        
    Returns:
        QualityValidationResult
    """
    validator = BusinessQualityValidator(config)
    return await validator.assess_content_quality(content_data, content_type)

# Export all classes and functions
__all__ = [
    'BusinessQualityValidator',
    'BusinessRuleType',
    'RuleSeverity',
    'ValidationContext',
    'QualityDimension',
    'QualityMetric',
    'QualityLevel',
    'BusinessRule',
    'BusinessValidationResult',
    'QualityScore',
    'QualityValidationResult',
    'validate_business_rules',
    'assess_content_quality'
]