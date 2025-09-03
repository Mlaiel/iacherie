"""Compatibility Score - Advanced Compatibility Scoring System

Sophisticated compatibility analysis system for evaluating creator partnerships
using multi-dimensional scoring, behavioral analysis, and success prediction.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import math

logger = logging.getLogger(__name__)


class CompatibilityDimension(Enum):
    """Dimensions of compatibility analysis"""
    SKILL_ALIGNMENT = "skill_alignment"
    CREATIVE_SYNERGY = "creative_synergy"
    WORK_STYLE = "work_style"
    COMMUNICATION = "communication"
    SCHEDULE_COMPATIBILITY = "schedule_compatibility"
    TECHNICAL_COMPATIBILITY = "technical_compatibility"
    CULTURAL_FIT = "cultural_fit"
    BUSINESS_ALIGNMENT = "business_alignment"
    REPUTATION_MATCH = "reputation_match"
    AUDIENCE_OVERLAP = "audience_overlap"


class ScoreConfidence(Enum):
    """Confidence levels for compatibility scores"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class DimensionScore:
    """Individual dimension compatibility score"""
    dimension: CompatibilityDimension
    score: float  # 0.0 to 1.0
    confidence: ScoreConfidence
    contributing_factors: List[str]
    improvement_suggestions: List[str]
    weight: float = 1.0
    raw_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompatibilityReport:
    """Comprehensive compatibility analysis report"""
    creator_a_id: str
    creator_b_id: str
    overall_score: float
    overall_confidence: ScoreConfidence
    dimension_scores: List[DimensionScore]
    strength_areas: List[str]
    concern_areas: List[str]
    collaboration_recommendations: List[str]
    risk_factors: List[str]
    success_predictors: List[str]
    optimal_collaboration_types: List[str]
    timeline_recommendations: str
    budget_implications: Dict[str, Any]
    report_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CreatorCompatibilityProfile:
    """Creator profile optimized for compatibility analysis"""
    creator_id: str
    work_preferences: Dict[str, Any]
    communication_style: Dict[str, float]
    technical_setup: Dict[str, Any]
    creative_approach: Dict[str, float]
    collaboration_history: List[Dict[str, Any]]
    schedule_patterns: Dict[str, Any]
    quality_standards: Dict[str, float]
    business_metrics: Dict[str, Any]
    cultural_attributes: Dict[str, Any]
    feedback_history: List[Dict[str, Any]]


class CompatibilityScore:
    """Advanced compatibility scoring system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Scoring weights for different dimensions
        self.dimension_weights = {
            CompatibilityDimension.SKILL_ALIGNMENT: 0.20,
            CompatibilityDimension.CREATIVE_SYNERGY: 0.15,
            CompatibilityDimension.WORK_STYLE: 0.12,
            CompatibilityDimension.COMMUNICATION: 0.12,
            CompatibilityDimension.SCHEDULE_COMPATIBILITY: 0.10,
            CompatibilityDimension.TECHNICAL_COMPATIBILITY: 0.08,
            CompatibilityDimension.CULTURAL_FIT: 0.08,
            CompatibilityDimension.BUSINESS_ALIGNMENT: 0.07,
            CompatibilityDimension.REPUTATION_MATCH: 0.05,
            CompatibilityDimension.AUDIENCE_OVERLAP: 0.03
        }
        
        # Confidence thresholds
        self.confidence_thresholds = {
            0.9: ScoreConfidence.VERY_HIGH,
            0.7: ScoreConfidence.HIGH,
            0.5: ScoreConfidence.MEDIUM,
            0.3: ScoreConfidence.LOW,
            0.0: ScoreConfidence.VERY_LOW
        }
        
        # Historical compatibility data for learning
        self.compatibility_history = []
        
        logger.info("CompatibilityScore system initialized with advanced scoring capabilities")
    
    async def initialize(self):
        """Initialize the compatibility scoring system"""
        logger.info("Initializing Compatibility Score system...")
        await self._load_historical_data()
        await self._calibrate_scoring_models()
        logger.info("Compatibility Score system initialized successfully")
    
    async def shutdown(self):
        """Shutdown the compatibility scoring system"""
        logger.info("Shutting down Compatibility Score system...")
        # Save learning data, cleanup resources
        logger.info("Compatibility Score system shutdown complete")
    
    async def calculate_compatibility(
        self, 
        profile_a: CreatorCompatibilityProfile, 
        profile_b: CreatorCompatibilityProfile
    ) -> CompatibilityReport:
        """Calculate comprehensive compatibility between two creators"""
        try:
            logger.info(f"Calculating compatibility between {profile_a.creator_id} and {profile_b.creator_id}")
            
            # Calculate scores for each dimension
            dimension_scores = []
            for dimension in CompatibilityDimension:
                score = await self._calculate_dimension_score(dimension, profile_a, profile_b)
                dimension_scores.append(score)
            
            # Calculate overall weighted score
            overall_score = self._calculate_overall_score(dimension_scores)
            
            # Determine overall confidence
            overall_confidence = self._determine_confidence(overall_score, dimension_scores)
            
            # Analyze strengths and concerns
            strength_areas = self._identify_strength_areas(dimension_scores)
            concern_areas = self._identify_concern_areas(dimension_scores)
            
            # Generate recommendations
            collaboration_recommendations = await self._generate_collaboration_recommendations(
                dimension_scores, profile_a, profile_b
            )
            
            # Identify risks and predictors
            risk_factors = await self._identify_risk_factors(dimension_scores, profile_a, profile_b)
            success_predictors = await self._identify_success_predictors(dimension_scores, profile_a, profile_b)
            
            # Recommend optimal collaboration types
            optimal_collaboration_types = await self._recommend_collaboration_types(
                dimension_scores, profile_a, profile_b
            )
            
            # Timeline and budget analysis
            timeline_recommendations = await self._analyze_timeline_compatibility(profile_a, profile_b)
            budget_implications = await self._analyze_budget_implications(dimension_scores, profile_a, profile_b)
            
            report = CompatibilityReport(
                creator_a_id=profile_a.creator_id,
                creator_b_id=profile_b.creator_id,
                overall_score=overall_score,
                overall_confidence=overall_confidence,
                dimension_scores=dimension_scores,
                strength_areas=strength_areas,
                concern_areas=concern_areas,
                collaboration_recommendations=collaboration_recommendations,
                risk_factors=risk_factors,
                success_predictors=success_predictors,
                optimal_collaboration_types=optimal_collaboration_types,
                timeline_recommendations=timeline_recommendations,
                budget_implications=budget_implications
            )
            
            # Store for learning
            self.compatibility_history.append(report)
            
            logger.info(f"Compatibility calculation completed: {overall_score:.2f} overall score")
            return report
            
        except Exception as e:
            logger.error(f"Error calculating compatibility: {str(e)}")
            raise
    
    async def _load_historical_data(self):
        """Load historical compatibility data for model calibration"""
        # In real implementation, load from database
        logger.info("Loading historical compatibility data...")
    
    async def _calibrate_scoring_models(self):
        """Calibrate scoring models based on historical data"""
        # In real implementation, use ML to optimize weights and thresholds
        logger.info("Calibrating compatibility scoring models...")
    
    async def _calculate_dimension_score(
        self, 
        dimension: CompatibilityDimension, 
        profile_a: CreatorCompatibilityProfile, 
        profile_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Calculate score for a specific compatibility dimension"""
        
        if dimension == CompatibilityDimension.SKILL_ALIGNMENT:
            return await self._score_skill_alignment(profile_a, profile_b)
        elif dimension == CompatibilityDimension.CREATIVE_SYNERGY:
            return await self._score_creative_synergy(profile_a, profile_b)
        elif dimension == CompatibilityDimension.WORK_STYLE:
            return await self._score_work_style(profile_a, profile_b)
        elif dimension == CompatibilityDimension.COMMUNICATION:
            return await self._score_communication(profile_a, profile_b)
        elif dimension == CompatibilityDimension.SCHEDULE_COMPATIBILITY:
            return await self._score_schedule_compatibility(profile_a, profile_b)
        elif dimension == CompatibilityDimension.TECHNICAL_COMPATIBILITY:
            return await self._score_technical_compatibility(profile_a, profile_b)
        elif dimension == CompatibilityDimension.CULTURAL_FIT:
            return await self._score_cultural_fit(profile_a, profile_b)
        elif dimension == CompatibilityDimension.BUSINESS_ALIGNMENT:
            return await self._score_business_alignment(profile_a, profile_b)
        elif dimension == CompatibilityDimension.REPUTATION_MATCH:
            return await self._score_reputation_match(profile_a, profile_b)
        elif dimension == CompatibilityDimension.AUDIENCE_OVERLAP:
            return await self._score_audience_overlap(profile_a, profile_b)
        else:
            # Default score
            return DimensionScore(
                dimension=dimension,
                score=0.5,
                confidence=ScoreConfidence.LOW,
                contributing_factors=["Unknown dimension"],
                improvement_suggestions=["Data not available"],
                weight=self.dimension_weights.get(dimension, 0.0)
            )
    
    async def _score_skill_alignment(
        self, 
        profile_a: CreatorCompatibilityProfile, 
        profile_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score skill alignment between creators"""
        
        # Extract skills from work preferences
        skills_a = set(profile_a.work_preferences.get('skills', []))
        skills_b = set(profile_b.work_preferences.get('skills', []))
        
        if not skills_a or not skills_b:
            return DimensionScore(
                dimension=CompatibilityDimension.SKILL_ALIGNMENT,
                score=0.5,
                confidence=ScoreConfidence.LOW,
                contributing_factors=["Limited skill data"],
                improvement_suggestions=["Complete skill profiles"],
                weight=self.dimension_weights[CompatibilityDimension.SKILL_ALIGNMENT]
            )
        
        # Calculate complementary skills score
        complementary_skills = 0
        overlapping_skills = len(skills_a.intersection(skills_b))
        total_unique_skills = len(skills_a.union(skills_b))
        
        # Look for complementary skills (this would be more sophisticated in real implementation)
        creative_skills = {'video_editing', 'graphic_design', 'photography', 'writing'}
        technical_skills = {'programming', 'web_development', 'analytics', 'seo'}
        marketing_skills = {'social_media', 'content_marketing', 'influencer_marketing'}
        
        skill_categories_a = {
            'creative': len(skills_a.intersection(creative_skills)),
            'technical': len(skills_a.intersection(technical_skills)),
            'marketing': len(skills_a.intersection(marketing_skills))
        }
        
        skill_categories_b = {
            'creative': len(skills_b.intersection(creative_skills)),
            'technical': len(skills_b.intersection(technical_skills)),
            'marketing': len(skills_b.intersection(marketing_skills))
        }
        
        # Calculate complementarity (high in different categories = good)
        complementarity = 0
        for category in skill_categories_a:
            if skill_categories_a[category] > 0 and skill_categories_b[category] == 0:
                complementarity += 0.3
            elif skill_categories_a[category] == 0 and skill_categories_b[category] > 0:
                complementarity += 0.3
        
        # Calculate overlap bonus (some overlap is good for communication)
        overlap_bonus = min(overlapping_skills / max(len(skills_a), len(skills_b)), 0.3)
        
        # Calculate final score
        skill_score = min((complementarity + overlap_bonus) / 1.2, 1.0)
        
        contributing_factors = []
        if overlapping_skills > 0:
            contributing_factors.append(f"{overlapping_skills} overlapping skills")
        if complementarity > 0.5:
            contributing_factors.append("Strong skill complementarity")
        
        improvement_suggestions = []
        if skill_score < 0.6:
            improvement_suggestions.append("Consider skill development in complementary areas")
        if overlapping_skills == 0:
            improvement_suggestions.append("Develop some shared skills for better communication")
        
        confidence = ScoreConfidence.HIGH if total_unique_skills > 5 else ScoreConfidence.MEDIUM
        
        return DimensionScore(
            dimension=CompatibilityDimension.SKILL_ALIGNMENT,
            score=skill_score,
            confidence=confidence,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.SKILL_ALIGNMENT],
            raw_metrics={
                'overlapping_skills': overlapping_skills,
                'complementarity_score': complementarity,
                'total_skills': total_unique_skills
            }
        )
    
    async def _score_creative_synergy(
        self, 
        profile_a: CreatorCompatibilityProfile, 
        profile_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score creative synergy potential"""
        
        # Extract creative approach metrics
        approach_a = profile_a.creative_approach
        approach_b = profile_b.creative_approach
        
        if not approach_a or not approach_b:
            return DimensionScore(
                dimension=CompatibilityDimension.CREATIVE_SYNERGY,
                score=0.5,
                confidence=ScoreConfidence.LOW,
                contributing_factors=["Limited creative approach data"],
                improvement_suggestions=["Complete creative profiles"],
                weight=self.dimension_weights[CompatibilityDimension.CREATIVE_SYNERGY]
            )
        
        # Compare creative styles
        style_compatibility = 0
        style_factors = ['innovation', 'collaboration_openness', 'risk_taking', 'perfectionism', 'speed_vs_quality']
        
        for factor in style_factors:
            if factor in approach_a and factor in approach_b:
                # Calculate similarity (for some factors) or complementarity (for others)
                diff = abs(approach_a[factor] - approach_b[factor])
                if factor in ['collaboration_openness', 'innovation']:
                    # These should be similar (high for both)
                    style_compatibility += (1 - diff) * 0.2
                else:
                    # These can be complementary
                    style_compatibility += min(diff, 1 - diff) * 0.2
        
        contributing_factors = []
        if style_compatibility > 0.7:
            contributing_factors.append("Strong creative style compatibility")
        if approach_a.get('collaboration_openness', 0) > 0.7 and approach_b.get('collaboration_openness', 0) > 0.7:
            contributing_factors.append("Both creators are open to collaboration")
        
        improvement_suggestions = []
        if style_compatibility < 0.5:
            improvement_suggestions.append("Discuss creative differences and find common ground")
        if approach_a.get('collaboration_openness', 0) < 0.5 or approach_b.get('collaboration_openness', 0) < 0.5:
            improvement_suggestions.append("Work on openness to collaborative creative processes")
        
        return DimensionScore(
            dimension=CompatibilityDimension.CREATIVE_SYNERGY,
            score=style_compatibility,
            confidence=ScoreConfidence.MEDIUM,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.CREATIVE_SYNERGY],
            raw_metrics={'style_compatibility': style_compatibility}
        )
    
    async def _score_work_style(
        self, 
        profile_a: CreatorCompatibilityProfile, 
        profile_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score work style compatibility"""
        
        prefs_a = profile_a.work_preferences
        prefs_b = profile_b.work_preferences
        
        work_style_score = 0.5  # Base score
        contributing_factors = []
        improvement_suggestions = []
        
        # Compare work preferences
        if 'work_schedule' in prefs_a and 'work_schedule' in prefs_b:
            schedule_a = prefs_a['work_schedule']
            schedule_b = prefs_b['work_schedule']
            
            # Check for schedule overlap
            overlap = self._calculate_schedule_overlap(schedule_a, schedule_b)
            work_style_score += overlap * 0.3
            
            if overlap > 0.5:
                contributing_factors.append("Good schedule overlap")
            else:
                improvement_suggestions.append("Consider adjusting schedules for better overlap")
        
        # Compare communication preferences
        if 'communication_freq' in prefs_a and 'communication_freq' in prefs_b:
            comm_diff = abs(prefs_a['communication_freq'] - prefs_b['communication_freq'])
            work_style_score += (1 - comm_diff) * 0.2
            
            if comm_diff < 0.3:
                contributing_factors.append("Similar communication frequency preferences")
        
        # Compare project management style
        if 'project_management_style' in prefs_a and 'project_management_style' in prefs_b:
            if prefs_a['project_management_style'] == prefs_b['project_management_style']:
                work_style_score += 0.2
                contributing_factors.append("Matching project management styles")
            else:
                improvement_suggestions.append("Discuss and align project management approaches")
        
        work_style_score = min(work_style_score, 1.0)
        
        return DimensionScore(
            dimension=CompatibilityDimension.WORK_STYLE,
            score=work_style_score,
            confidence=ScoreConfidence.MEDIUM,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.WORK_STYLE]
        )
    
    async def _score_communication(
        self, 
        profile_a: CreatorCompatibilityProfile, 
        profile_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score communication compatibility"""
        
        comm_a = profile_a.communication_style
        comm_b = profile_b.communication_style
        
        if not comm_a or not comm_b:
            return DimensionScore(
                dimension=CompatibilityDimension.COMMUNICATION,
                score=0.5,
                confidence=ScoreConfidence.LOW,
                contributing_factors=["Limited communication style data"],
                improvement_suggestions=["Complete communication profiles"],
                weight=self.dimension_weights[CompatibilityDimension.COMMUNICATION]
            )
        
        # Compare communication styles
        comm_score = 0
        factors = ['directness', 'formality', 'responsiveness', 'detail_level', 'feedback_style']
        
        for factor in factors:
            if factor in comm_a and factor in comm_b:
                diff = abs(comm_a[factor] - comm_b[factor])
                # For communication, similarity is generally better
                comm_score += (1 - diff) * (1 / len(factors))
        
        contributing_factors = []
        improvement_suggestions = []
        
        if comm_score > 0.7:
            contributing_factors.append("Strong communication style alignment")
        
        # Check specific compatibility factors
        if comm_a.get('responsiveness', 0) > 0.7 and comm_b.get('responsiveness', 0) > 0.7:
            contributing_factors.append("Both creators are responsive communicators")
        elif comm_a.get('responsiveness', 0) < 0.4 or comm_b.get('responsiveness', 0) < 0.4:
            improvement_suggestions.append("Improve communication responsiveness")
        
        return DimensionScore(
            dimension=CompatibilityDimension.COMMUNICATION,
            score=comm_score,
            confidence=ScoreConfidence.MEDIUM,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.COMMUNICATION]
        )
    
    async def _score_schedule_compatibility(
        self, 
        profile_a: CreatorCompatibilityProfile, 
        profile_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score schedule compatibility"""
        
        schedule_a = profile_a.schedule_patterns
        schedule_b = profile_b.schedule_patterns
        
        if not schedule_a or not schedule_b:
            return DimensionScore(
                dimension=CompatibilityDimension.SCHEDULE_COMPATIBILITY,
                score=0.5,
                confidence=ScoreConfidence.LOW,
                contributing_factors=["Limited schedule data"],
                improvement_suggestions=["Share schedule information"],
                weight=self.dimension_weights[CompatibilityDimension.SCHEDULE_COMPATIBILITY]
            )
        
        # Calculate schedule overlap
        overlap_score = 0
        contributing_factors = []
        improvement_suggestions = []
        
        # Time zone compatibility
        tz_a = schedule_a.get('timezone', 'UTC')
        tz_b = schedule_b.get('timezone', 'UTC')
        
        if tz_a == tz_b:
            overlap_score += 0.3
            contributing_factors.append("Same timezone")
        else:
            # Calculate time zone difference impact
            tz_diff = abs(self._calculate_timezone_difference(tz_a, tz_b))
            if tz_diff <= 3:
                overlap_score += 0.2
                contributing_factors.append("Compatible timezones")
            else:
                improvement_suggestions.append("Consider scheduling challenges due to timezone difference")
        
        # Working hours overlap
        hours_a = schedule_a.get('working_hours', [9, 17])  # Default 9 AM to 5 PM
        hours_b = schedule_b.get('working_hours', [9, 17])
        
        overlap_hours = max(0, min(hours_a[1], hours_b[1]) - max(hours_a[0], hours_b[0]))
        max_possible_overlap = min(hours_a[1] - hours_a[0], hours_b[1] - hours_b[0])
        
        if max_possible_overlap > 0:
            hours_overlap = overlap_hours / max_possible_overlap
            overlap_score += hours_overlap * 0.4
            
            if hours_overlap > 0.5:
                contributing_factors.append(f"{overlap_hours} hours of working time overlap")
            else:
                improvement_suggestions.append("Limited working hours overlap")
        
        # Availability patterns
        if 'availability' in schedule_a and 'availability' in schedule_b:
            avail_a = schedule_a['availability']
            avail_b = schedule_b['availability']
            
            common_days = set(avail_a.keys()).intersection(set(avail_b.keys()))
            if common_days:
                overlap_score += min(len(common_days) / 7, 0.3)
                contributing_factors.append(f"Available on {len(common_days)} common days")
        
        overlap_score = min(overlap_score, 1.0)
        
        return DimensionScore(
            dimension=CompatibilityDimension.SCHEDULE_COMPATIBILITY,
            score=overlap_score,
            confidence=ScoreConfidence.MEDIUM,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.SCHEDULE_COMPATIBILITY]
        )
    
    async def _score_technical_compatibility(
        self, 
        profile_a: CreatorCompatibilityProfile, 
        profile_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score technical setup compatibility"""
        
        tech_a = profile_a.technical_setup
        tech_b = profile_b.technical_setup
        
        if not tech_a or not tech_b:
            return DimensionScore(
                dimension=CompatibilityDimension.TECHNICAL_COMPATIBILITY,
                score=0.5,
                confidence=ScoreConfidence.LOW,
                contributing_factors=["Limited technical setup data"],
                improvement_suggestions=["Share technical setup information"],
                weight=self.dimension_weights[CompatibilityDimension.TECHNICAL_COMPATIBILITY]
            )
        
        tech_score = 0.5  # Base score
        contributing_factors = []
        improvement_suggestions = []
        
        # Software compatibility
        software_a = set(tech_a.get('software', []))
        software_b = set(tech_b.get('software', []))
        
        if software_a and software_b:
            common_software = software_a.intersection(software_b)
            total_software = software_a.union(software_b)
            
            if common_software:
                compatibility_ratio = len(common_software) / len(total_software)
                tech_score += compatibility_ratio * 0.3
                contributing_factors.append(f"{len(common_software)} shared software tools")
            else:
                improvement_suggestions.append("Consider adopting common software tools")
        
        # Hardware compatibility
        equipment_a = set(tech_a.get('equipment', []))
        equipment_b = set(tech_b.get('equipment', []))
        
        if equipment_a and equipment_b:
            common_equipment = equipment_a.intersection(equipment_b)
            if common_equipment:
                tech_score += 0.2
                contributing_factors.append("Compatible equipment setup")
        
        # Quality standards alignment
        quality_a = tech_a.get('quality_standards', {})
        quality_b = tech_b.get('quality_standards', {})
        
        if quality_a and quality_b:
            quality_alignment = self._calculate_quality_alignment(quality_a, quality_b)
            tech_score += quality_alignment * 0.3
            
            if quality_alignment > 0.7:
                contributing_factors.append("Aligned quality standards")
            else:
                improvement_suggestions.append("Discuss and align quality standards")
        
        tech_score = min(tech_score, 1.0)
        
        return DimensionScore(
            dimension=CompatibilityDimension.TECHNICAL_COMPATIBILITY,
            score=tech_score,
            confidence=ScoreConfidence.MEDIUM,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.TECHNICAL_COMPATIBILITY]
        )
    
    async def _score_cultural_fit(
        self, 
        profile_a: CreatorCompatibilityProfile, 
        profile_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score cultural fit between creators"""
        
        culture_a = profile_a.cultural_attributes
        culture_b = profile_b.cultural_attributes
        
        if not culture_a or not culture_b:
            return DimensionScore(
                dimension=CompatibilityDimension.CULTURAL_FIT,
                score=0.7,  # Neutral positive assumption
                confidence=ScoreConfidence.LOW,
                contributing_factors=["Limited cultural data"],
                improvement_suggestions=["Share cultural preferences"],
                weight=self.dimension_weights[CompatibilityDimension.CULTURAL_FIT]
            )
        
        cultural_score = 0.5
        contributing_factors = []
        improvement_suggestions = []
        
        # Values alignment
        values_a = culture_a.get('values', [])
        values_b = culture_b.get('values', [])
        
        if values_a and values_b:
            common_values = set(values_a).intersection(set(values_b))
            if common_values:
                cultural_score += min(len(common_values) / max(len(values_a), len(values_b)), 0.3)
                contributing_factors.append(f"Shared values: {', '.join(common_values)}")
        
        # Work culture preferences
        work_culture_a = culture_a.get('work_culture', {})
        work_culture_b = culture_b.get('work_culture', {})
        
        if work_culture_a and work_culture_b:
            culture_factors = ['hierarchy', 'formality', 'innovation', 'collaboration']
            alignment = 0
            
            for factor in culture_factors:
                if factor in work_culture_a and factor in work_culture_b:
                    diff = abs(work_culture_a[factor] - work_culture_b[factor])
                    alignment += (1 - diff) / len(culture_factors)
            
            cultural_score += alignment * 0.4
            
            if alignment > 0.7:
                contributing_factors.append("Strong work culture alignment")
        
        cultural_score = min(cultural_score, 1.0)
        
        return DimensionScore(
            dimension=CompatibilityDimension.CULTURAL_FIT,
            score=cultural_score,
            confidence=ScoreConfidence.MEDIUM,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.CULTURAL_FIT]
        )
    
    async def _score_business_alignment(
        self, 
        profile_a: CreatorCompatibilityProfile, 
        profile_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score business goals and metrics alignment"""
        
        business_a = profile_a.business_metrics
        business_b = profile_b.business_metrics
        
        if not business_a or not business_b:
            return DimensionScore(
                dimension=CompatibilityDimension.BUSINESS_ALIGNMENT,
                score=0.5,
                confidence=ScoreConfidence.LOW,
                contributing_factors=["Limited business metrics data"],
                improvement_suggestions=["Share business goals and metrics"],
                weight=self.dimension_weights[CompatibilityDimension.BUSINESS_ALIGNMENT]
            )
        
        business_score = 0.5
        contributing_factors = []
        improvement_suggestions = []
        
        # Goals alignment
        goals_a = business_a.get('goals', [])
        goals_b = business_b.get('goals', [])
        
        if goals_a and goals_b:
            common_goals = set(goals_a).intersection(set(goals_b))
            if common_goals:
                business_score += min(len(common_goals) / max(len(goals_a), len(goals_b)), 0.3)
                contributing_factors.append(f"Shared goals: {', '.join(common_goals)}")
        
        # Budget/revenue alignment
        budget_a = business_a.get('budget_range', [0, 1000])
        budget_b = business_b.get('budget_range', [0, 1000])
        
        budget_overlap = max(0, min(budget_a[1], budget_b[1]) - max(budget_a[0], budget_b[0]))
        budget_union = max(budget_a[1], budget_b[1]) - min(budget_a[0], budget_b[0])
        
        if budget_union > 0:
            budget_compatibility = budget_overlap / budget_union
            business_score += budget_compatibility * 0.2
            
            if budget_compatibility > 0.5:
                contributing_factors.append("Compatible budget ranges")
            else:
                improvement_suggestions.append("Discuss budget expectations")
        
        business_score = min(business_score, 1.0)
        
        return DimensionScore(
            dimension=CompatibilityDimension.BUSINESS_ALIGNMENT,
            score=business_score,
            confidence=ScoreConfidence.MEDIUM,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.BUSINESS_ALIGNMENT]
        )
    
    async def _score_reputation_match(
        self, 
        profile_a: CreatorCompatibilityProfile, 
        profile_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score reputation compatibility"""
        
        # Extract reputation scores from feedback history
        feedback_a = profile_a.feedback_history
        feedback_b = profile_b.feedback_history
        
        if not feedback_a or not feedback_b:
            return DimensionScore(
                dimension=CompatibilityDimension.REPUTATION_MATCH,
                score=0.7,  # Neutral positive
                confidence=ScoreConfidence.LOW,
                contributing_factors=["Limited feedback history"],
                improvement_suggestions=["Build feedback history"],
                weight=self.dimension_weights[CompatibilityDimension.REPUTATION_MATCH]
            )
        
        # Calculate average ratings
        ratings_a = [feedback.get('rating', 0) for feedback in feedback_a]
        ratings_b = [feedback.get('rating', 0) for feedback in feedback_b]
        
        avg_rating_a = sum(ratings_a) / len(ratings_a) if ratings_a else 0
        avg_rating_b = sum(ratings_b) / len(ratings_b) if ratings_b else 0
        
        # Reputation compatibility (similar reputation levels work better)
        rating_diff = abs(avg_rating_a - avg_rating_b)
        reputation_score = max(0, 1 - (rating_diff / 5))  # Assuming 5-point rating scale
        
        contributing_factors = []
        if avg_rating_a > 4 and avg_rating_b > 4:
            contributing_factors.append("Both creators have excellent ratings")
        elif avg_rating_a > 3.5 and avg_rating_b > 3.5:
            contributing_factors.append("Both creators have good ratings")
        
        improvement_suggestions = []
        if rating_diff > 1.0:
            improvement_suggestions.append("Large reputation gap may affect collaboration dynamics")
        
        return DimensionScore(
            dimension=CompatibilityDimension.REPUTATION_MATCH,
            score=reputation_score,
            confidence=ScoreConfidence.MEDIUM,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.REPUTATION_MATCH]
        )
    
    async def _score_audience_overlap(
        self, 
        profile_a: CreatorCompatibilityProfile, 
        profile_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score audience overlap (some overlap is good, too much might not be)"""
        
        # This would typically come from social media analytics
        # For now, use business metrics as proxy
        business_a = profile_a.business_metrics
        business_b = profile_b.business_metrics
        
        if not business_a or not business_b:
            return DimensionScore(
                dimension=CompatibilityDimension.AUDIENCE_OVERLAP,
                score=0.5,
                confidence=ScoreConfidence.LOW,
                contributing_factors=["Limited audience data"],
                improvement_suggestions=["Share audience analytics"],
                weight=self.dimension_weights[CompatibilityDimension.AUDIENCE_OVERLAP]
            )
        
        # Extract audience information
        audience_a = business_a.get('target_audience', {})
        audience_b = business_b.get('target_audience', {})
        
        if not audience_a or not audience_b:
            return DimensionScore(
                dimension=CompatibilityDimension.AUDIENCE_OVERLAP,
                score=0.5,
                confidence=ScoreConfidence.LOW,
                contributing_factors=["Limited audience targeting data"],
                improvement_suggestions=["Define target audience"],
                weight=self.dimension_weights[CompatibilityDimension.AUDIENCE_OVERLAP]
            )
        
        # Calculate overlap in demographics
        overlap_score = 0.5
        contributing_factors = []
        
        # Age group overlap
        age_a = audience_a.get('age_groups', [])
        age_b = audience_b.get('age_groups', [])
        if age_a and age_b:
            age_overlap = len(set(age_a).intersection(set(age_b))) / len(set(age_a).union(set(age_b)))
            # Moderate overlap (30-70%) is ideal
            if 0.3 <= age_overlap <= 0.7:
                overlap_score += 0.3
                contributing_factors.append("Good age group overlap")
            elif age_overlap > 0.7:
                overlap_score += 0.1
                contributing_factors.append("High age group overlap")
        
        # Interest overlap
        interests_a = audience_a.get('interests', [])
        interests_b = audience_b.get('interests', [])
        if interests_a and interests_b:
            interest_overlap = len(set(interests_a).intersection(set(interests_b))) / len(set(interests_a).union(set(interests_b)))
            if 0.2 <= interest_overlap <= 0.6:
                overlap_score += 0.2
                contributing_factors.append("Complementary audience interests")
        
        overlap_score = min(overlap_score, 1.0)
        
        return DimensionScore(
            dimension=CompatibilityDimension.AUDIENCE_OVERLAP,
            score=overlap_score,
            confidence=ScoreConfidence.MEDIUM,
            contributing_factors=contributing_factors,
            improvement_suggestions=[],
            weight=self.dimension_weights[CompatibilityDimension.AUDIENCE_OVERLAP]
        )
    
    def _calculate_overall_score(self, dimension_scores: List[DimensionScore]) -> float:
        """Calculate weighted overall compatibility score"""
        total_weighted_score = 0
        total_weight = 0
        
        for score in dimension_scores:
            total_weighted_score += score.score * score.weight
            total_weight += score.weight
        
        return total_weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_confidence(self, overall_score: float, dimension_scores: List[DimensionScore]) -> ScoreConfidence:
        """Determine overall confidence based on score and individual confidences"""
        
        # Calculate average confidence
        confidence_values = {
            ScoreConfidence.VERY_LOW: 0.1,
            ScoreConfidence.LOW: 0.3,
            ScoreConfidence.MEDIUM: 0.5,
            ScoreConfidence.HIGH: 0.7,
            ScoreConfidence.VERY_HIGH: 0.9
        }
        
        avg_confidence = sum(confidence_values[score.confidence] for score in dimension_scores) / len(dimension_scores)
        
        # Adjust based on overall score consistency
        for threshold, confidence in sorted(self.confidence_thresholds.items(), reverse=True):
            if avg_confidence >= threshold:
                return confidence
        
        return ScoreConfidence.VERY_LOW
    
    def _identify_strength_areas(self, dimension_scores: List[DimensionScore]) -> List[str]:
        """Identify top strength areas"""
        sorted_scores = sorted(dimension_scores, key=lambda x: x.score, reverse=True)
        strengths = []
        
        for score in sorted_scores[:3]:  # Top 3
            if score.score > 0.7:
                strengths.append(f"{score.dimension.value.replace('_', ' ').title()}: {score.score:.2f}")
        
        return strengths
    
    def _identify_concern_areas(self, dimension_scores: List[DimensionScore]) -> List[str]:
        """Identify areas of concern"""
        concerns = []
        
        for score in dimension_scores:
            if score.score < 0.4:
                concerns.append(f"{score.dimension.value.replace('_', ' ').title()}: {score.score:.2f}")
        
        return concerns
    
    async def _generate_collaboration_recommendations(
        self, 
        dimension_scores: List[DimensionScore], 
        profile_a: CreatorCompatibilityProfile, 
        profile_b: CreatorCompatibilityProfile
    ) -> List[str]:
        """Generate collaboration recommendations"""
        recommendations = []
        
        # Analyze scores to generate specific recommendations
        for score in dimension_scores:
            if score.score < 0.5:
                recommendations.extend(score.improvement_suggestions)
        
        # Add general recommendations based on overall compatibility
        overall_score = self._calculate_overall_score(dimension_scores)
        
        if overall_score > 0.8:
            recommendations.append("Excellent compatibility - proceed with confidence")
        elif overall_score > 0.6:
            recommendations.append("Good compatibility - address minor concerns before proceeding")
        else:
            recommendations.append("Consider additional alignment discussions before collaboration")
        
        return recommendations[:5]  # Limit to top 5
    
    async def _identify_risk_factors(
        self, 
        dimension_scores: List[DimensionScore], 
        profile_a: CreatorCompatibilityProfile, 
        profile_b: CreatorCompatibilityProfile
    ) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        for score in dimension_scores:
            if score.score < 0.3:
                risks.append(f"Low {score.dimension.value.replace('_', ' ')}")
        
        # Specific risk patterns
        comm_score = next((s.score for s in dimension_scores if s.dimension == CompatibilityDimension.COMMUNICATION), 0.5)
        schedule_score = next((s.score for s in dimension_scores if s.dimension == CompatibilityDimension.SCHEDULE_COMPATIBILITY), 0.5)
        
        if comm_score < 0.4 and schedule_score < 0.4:
            risks.append("Communication and scheduling challenges may compound")
        
        return risks
    
    async def _identify_success_predictors(
        self, 
        dimension_scores: List[DimensionScore], 
        profile_a: CreatorCompatibilityProfile, 
        profile_b: CreatorCompatibilityProfile
    ) -> List[str]:
        """Identify success predictors"""
        predictors = []
        
        for score in dimension_scores:
            if score.score > 0.8:
                predictors.append(f"Strong {score.dimension.value.replace('_', ' ')}")
        
        # Look for positive patterns
        skill_score = next((s.score for s in dimension_scores if s.dimension == CompatibilityDimension.SKILL_ALIGNMENT), 0.5)
        creative_score = next((s.score for s in dimension_scores if s.dimension == CompatibilityDimension.CREATIVE_SYNERGY), 0.5)
        
        if skill_score > 0.7 and creative_score > 0.7:
            predictors.append("Strong skill and creative alignment suggests high success potential")
        
        return predictors
    
    async def _recommend_collaboration_types(
        self, 
        dimension_scores: List[DimensionScore], 
        profile_a: CreatorCompatibilityProfile, 
        profile_b: CreatorCompatibilityProfile
    ) -> List[str]:
        """Recommend optimal collaboration types"""
        recommendations = []
        
        # Analyze dimension scores to recommend collaboration types
        skill_score = next((s.score for s in dimension_scores if s.dimension == CompatibilityDimension.SKILL_ALIGNMENT), 0.5)
        creative_score = next((s.score for s in dimension_scores if s.dimension == CompatibilityDimension.CREATIVE_SYNERGY), 0.5)
        schedule_score = next((s.score for s in dimension_scores if s.dimension == CompatibilityDimension.SCHEDULE_COMPATIBILITY), 0.5)
        
        if skill_score > 0.7 and creative_score > 0.7:
            recommendations.append("Joint Content Creation")
        
        if schedule_score > 0.6:
            recommendations.append("Real-time Collaboration")
        
        if skill_score > 0.6:
            recommendations.append("Skill Exchange Partnership")
        
        # Default recommendations
        recommendations.extend(["Cross-promotion", "Guest appearances"])
        
        return recommendations[:3]
    
    async def _analyze_timeline_compatibility(
        self, 
        profile_a: CreatorCompatibilityProfile, 
        profile_b: CreatorCompatibilityProfile
    ) -> str:
        """Analyze and recommend timeline"""
        
        schedule_a = profile_a.schedule_patterns
        schedule_b = profile_b.schedule_patterns
        
        if not schedule_a or not schedule_b:
            return "Timeline analysis requires schedule information from both creators"
        
        # Analyze availability patterns
        availability_a = schedule_a.get('availability', {})
        availability_b = schedule_b.get('availability', {})
        
        if availability_a and availability_b:
            common_availability = set(availability_a.keys()).intersection(set(availability_b.keys()))
            
            if len(common_availability) >= 4:
                return "Flexible timeline possible with good availability overlap"
            elif len(common_availability) >= 2:
                return "Moderate timeline flexibility - plan around common availability"
            else:
                return "Limited timeline flexibility - requires careful scheduling"
        
        return "Standard timeline recommended - coordinate schedules carefully"
    
    async def _analyze_budget_implications(
        self, 
        dimension_scores: List[DimensionScore], 
        profile_a: CreatorCompatibilityProfile, 
        profile_b: CreatorCompatibilityProfile
    ) -> Dict[str, Any]:
        """Analyze budget implications"""
        
        implications = {
            'budget_risk': 'medium',
            'cost_factors': [],
            'savings_opportunities': [],
            'recommendations': []
        }
        
        # Analyze technical compatibility for cost implications
        tech_score = next((s.score for s in dimension_scores if s.dimension == CompatibilityDimension.TECHNICAL_COMPATIBILITY), 0.5)
        
        if tech_score < 0.5:
            implications['cost_factors'].append("Technical setup alignment may require additional investment")
            implications['budget_risk'] = 'high'
        elif tech_score > 0.8:
            implications['savings_opportunities'].append("High technical compatibility may reduce setup costs")
        
        # Analyze schedule compatibility for cost implications
        schedule_score = next((s.score for s in dimension_scores if s.dimension == CompatibilityDimension.SCHEDULE_COMPATIBILITY), 0.5)
        
        if schedule_score < 0.4:
            implications['cost_factors'].append("Schedule misalignment may increase coordination costs")
        
        # Generate recommendations
        if implications['budget_risk'] == 'high':
            implications['recommendations'].append("Budget additional 15-20% for alignment activities")
        elif implications['budget_risk'] == 'medium':
            implications['recommendations'].append("Budget standard collaboration costs with 10% contingency")
        else:
            implications['recommendations'].append("Standard collaboration budget should be sufficient")
        
        return implications
    
    # Helper methods
    
    def _calculate_schedule_overlap(self, schedule_a: Dict, schedule_b: Dict) -> float:
        """Calculate schedule overlap percentage"""
        # Simplified calculation - in real implementation, this would be more sophisticated
        if not schedule_a or not schedule_b:
            return 0.5
        
        # For this example, assume some overlap logic
        return 0.6  # Placeholder
    
    def _calculate_timezone_difference(self, tz_a: str, tz_b: str) -> int:
        """Calculate timezone difference in hours"""
        # Simplified - in real implementation, use proper timezone library
        tz_offsets = {
            'UTC': 0, 'EST': -5, 'PST': -8, 'CET': 1, 'JST': 9
        }
        
        offset_a = tz_offsets.get(tz_a, 0)
        offset_b = tz_offsets.get(tz_b, 0)
        
        return abs(offset_a - offset_b)
    
    def _calculate_quality_alignment(self, quality_a: Dict, quality_b: Dict) -> float:
        """Calculate quality standards alignment"""
        if not quality_a or not quality_b:
            return 0.5
        
        # Compare quality metrics
        alignment = 0
        factors = ['video_quality', 'audio_quality', 'content_quality', 'production_value']
        
        for factor in factors:
            if factor in quality_a and factor in quality_b:
                diff = abs(quality_a[factor] - quality_b[factor])
                alignment += (1 - diff) / len(factors)
        
        return alignment


# Export main classes
__all__ = [
    'CompatibilityScore', 'CompatibilityReport', 'DimensionScore', 'CreatorCompatibilityProfile',
    'CompatibilityDimension', 'ScoreConfidence'
]