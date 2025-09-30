"""Compatibility Scorer - Advanced Compatibility Scoring System

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


class CompatibilityScorer:
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
            ScoreConfidence.VERY_LOW: (0.0, 0.2),
            ScoreConfidence.LOW: (0.2, 0.4),
            ScoreConfidence.MEDIUM: (0.4, 0.6),
            ScoreConfidence.HIGH: (0.6, 0.8),
            ScoreConfidence.VERY_HIGH: (0.8, 1.0)
        }
        
        logger.info("CompatibilityScorer initialized with multi-dimensional analysis")
    
    async def analyze_compatibility(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile,
        collaboration_context: Optional[Dict[str, Any]] = None
    ) -> CompatibilityReport:
        """Perform comprehensive compatibility analysis between two creators"""
        try:
            logger.info(f"Analyzing compatibility between {creator_a.creator_id} and {creator_b.creator_id}")
            
            # Score each dimension
            dimension_scores = []
            
            for dimension in CompatibilityDimension:
                score = await self._score_dimension(
                    dimension, creator_a, creator_b, collaboration_context
                )
                dimension_scores.append(score)
            
            # Calculate overall score
            overall_score = await self._calculate_overall_score(dimension_scores)
            
            # Determine overall confidence
            overall_confidence = await self._calculate_overall_confidence(dimension_scores)
            
            # Identify strengths and concerns
            strength_areas = await self._identify_strength_areas(dimension_scores)
            concern_areas = await self._identify_concern_areas(dimension_scores)
            
            # Generate recommendations
            collaboration_recommendations = await self._generate_collaboration_recommendations(
                dimension_scores, creator_a, creator_b
            )
            
            # Identify risk factors and success predictors
            risk_factors = await self._identify_risk_factors(dimension_scores, creator_a, creator_b)
            success_predictors = await self._identify_success_predictors(dimension_scores, creator_a, creator_b)
            
            # Recommend optimal collaboration types
            optimal_collaboration_types = await self._recommend_collaboration_types(
                dimension_scores, creator_a, creator_b
            )
            
            # Generate timeline recommendations
            timeline_recommendations = await self._generate_timeline_recommendations(
                dimension_scores, creator_a, creator_b
            )
            
            # Analyze budget implications
            budget_implications = await self._analyze_budget_implications(
                dimension_scores, creator_a, creator_b
            )
            
            report = CompatibilityReport(
                creator_a_id=creator_a.creator_id,
                creator_b_id=creator_b.creator_id,
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
            
            logger.info(f"Compatibility analysis completed: {overall_score:.3f} overall score")
            return report
            
        except Exception as e:
            logger.error(f"Compatibility analysis failed: {e}")
            raise
    
    async def _score_dimension(
        self,
        dimension: CompatibilityDimension,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile,
        collaboration_context: Optional[Dict[str, Any]] = None
    ) -> DimensionScore:
        """Score a specific compatibility dimension"""
        if dimension == CompatibilityDimension.SKILL_ALIGNMENT:
            return await self._score_skill_alignment(creator_a, creator_b)
        elif dimension == CompatibilityDimension.CREATIVE_SYNERGY:
            return await self._score_creative_synergy(creator_a, creator_b)
        elif dimension == CompatibilityDimension.WORK_STYLE:
            return await self._score_work_style(creator_a, creator_b)
        elif dimension == CompatibilityDimension.COMMUNICATION:
            return await self._score_communication(creator_a, creator_b)
        elif dimension == CompatibilityDimension.SCHEDULE_COMPATIBILITY:
            return await self._score_schedule_compatibility(creator_a, creator_b)
        elif dimension == CompatibilityDimension.TECHNICAL_COMPATIBILITY:
            return await self._score_technical_compatibility(creator_a, creator_b)
        elif dimension == CompatibilityDimension.CULTURAL_FIT:
            return await self._score_cultural_fit(creator_a, creator_b)
        elif dimension == CompatibilityDimension.BUSINESS_ALIGNMENT:
            return await self._score_business_alignment(creator_a, creator_b)
        elif dimension == CompatibilityDimension.REPUTATION_MATCH:
            return await self._score_reputation_match(creator_a, creator_b)
        elif dimension == CompatibilityDimension.AUDIENCE_OVERLAP:
            return await self._score_audience_overlap(creator_a, creator_b)
        else:
            # Default scoring
            return DimensionScore(
                dimension=dimension,
                score=0.5,
                confidence=ScoreConfidence.MEDIUM,
                contributing_factors=["Default scoring applied"],
                improvement_suggestions=["Implement specific scoring logic"]
            )
    
    async def _score_skill_alignment(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score skill alignment compatibility"""
        # Analyze skill complementarity and overlap
        work_prefs_a = creator_a.work_preferences
        work_prefs_b = creator_b.work_preferences
        
        skills_a = set(work_prefs_a.get('skills', []))
        skills_b = set(work_prefs_b.get('skills', []))
        
        # Calculate skill overlap and complementarity
        skill_overlap = len(skills_a.intersection(skills_b))
        total_skills = len(skills_a.union(skills_b))
        unique_skills_each = len(skills_a.symmetric_difference(skills_b))
        
        # Scoring logic
        if total_skills == 0:
            overlap_score = 0.5
        else:
            # Moderate overlap is good, too much overlap or too little is bad
            overlap_ratio = skill_overlap / total_skills
            if 0.3 <= overlap_ratio <= 0.7:
                overlap_score = 1.0
            else:
                overlap_score = 1.0 - abs(overlap_ratio - 0.5) * 2
        
        # Complementarity bonus
        complementarity_score = min(1.0, unique_skills_each / max(total_skills, 1))
        
        # Quality levels alignment
        quality_a = creator_a.quality_standards
        quality_b = creator_b.quality_standards
        
        quality_alignment = 0.0
        quality_count = 0
        for aspect in ['technical_quality', 'creative_quality', 'delivery_quality']:
            if aspect in quality_a and aspect in quality_b:
                diff = abs(quality_a[aspect] - quality_b[aspect])
                quality_alignment += 1.0 - diff
                quality_count += 1
        
        if quality_count > 0:
            quality_score = quality_alignment / quality_count
        else:
            quality_score = 0.7  # Default moderate alignment
        
        # Combined score
        final_score = (overlap_score * 0.4 + complementarity_score * 0.3 + quality_score * 0.3)
        
        # Contributing factors
        contributing_factors = []
        if overlap_score > 0.7:
            contributing_factors.append(f"Good skill overlap ({skill_overlap} shared skills)")
        if complementarity_score > 0.7:
            contributing_factors.append(f"Strong skill complementarity ({unique_skills_each} unique skills)")
        if quality_score > 0.8:
            contributing_factors.append("Well-aligned quality standards")
        
        # Improvement suggestions
        improvement_suggestions = []
        if overlap_score < 0.5:
            improvement_suggestions.append("Consider cross-training in complementary skills")
        if quality_score < 0.6:
            improvement_suggestions.append("Establish common quality standards and expectations")
        
        # Determine confidence
        confidence = self._determine_confidence(final_score, len(contributing_factors))
        
        return DimensionScore(
            dimension=CompatibilityDimension.SKILL_ALIGNMENT,
            score=round(final_score, 3),
            confidence=confidence,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.SKILL_ALIGNMENT],
            raw_metrics={
                'overlap_score': overlap_score,
                'complementarity_score': complementarity_score,
                'quality_score': quality_score,
                'shared_skills': list(skills_a.intersection(skills_b)),
                'unique_skills': list(skills_a.symmetric_difference(skills_b))
            }
        )
    
    async def _score_creative_synergy(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score creative synergy potential"""
        creative_a = creator_a.creative_approach
        creative_b = creator_b.creative_approach
        
        synergy_factors = []
        
        # Creative style compatibility
        style_compatibility = 0.0
        style_count = 0
        
        for aspect in ['innovation', 'risk_taking', 'experimentation', 'structure_preference']:
            if aspect in creative_a and aspect in creative_b:
                # For creativity, some difference can be beneficial
                diff = abs(creative_a[aspect] - creative_b[aspect])
                if diff < 0.2:  # Very similar
                    compatibility = 0.8
                elif diff < 0.5:  # Complementary
                    compatibility = 1.0
                else:  # Too different
                    compatibility = 0.4
                
                style_compatibility += compatibility
                style_count += 1
        
        if style_count > 0:
            style_score = style_compatibility / style_count
        else:
            style_score = 0.6
        
        synergy_factors.append(style_score)
        
        # Creative process compatibility
        process_prefs_a = creator_a.work_preferences.get('creative_process', {})
        process_prefs_b = creator_b.work_preferences.get('creative_process', {})
        
        process_alignment = 0.0
        process_count = 0
        
        for aspect in ['planning_level', 'feedback_frequency', 'iteration_preference']:
            if aspect in process_prefs_a and aspect in process_prefs_b:
                diff = abs(process_prefs_a[aspect] - process_prefs_b[aspect])
                process_alignment += 1.0 - diff
                process_count += 1
        
        if process_count > 0:
            process_score = process_alignment / process_count
        else:
            process_score = 0.6
        
        synergy_factors.append(process_score)
        
        # Previous collaboration outcomes
        history_a = creator_a.collaboration_history
        history_b = creator_b.collaboration_history
        
        if history_a and history_b:
            # Analyze success patterns
            success_rate_a = sum(1 for collab in history_a if collab.get('success_rating', 3) > 3) / len(history_a)
            success_rate_b = sum(1 for collab in history_b if collab.get('success_rating', 3) > 3) / len(history_b)
            
            history_score = (success_rate_a + success_rate_b) / 2
        else:
            history_score = 0.5  # Neutral for new collaborators
        
        synergy_factors.append(history_score)
        
        # Final synergy score
        final_score = sum(synergy_factors) / len(synergy_factors)
        
        # Contributing factors
        contributing_factors = []
        if style_score > 0.8:
            contributing_factors.append("Complementary creative styles")
        if process_score > 0.7:
            contributing_factors.append("Aligned creative processes")
        if history_score > 0.7:
            contributing_factors.append("Strong collaboration track records")
        
        # Improvement suggestions
        improvement_suggestions = []
        if style_score < 0.6:
            improvement_suggestions.append("Discuss and align on creative vision and approaches")
        if process_score < 0.6:
            improvement_suggestions.append("Establish clear creative workflow and feedback processes")
        
        confidence = self._determine_confidence(final_score, len(contributing_factors))
        
        return DimensionScore(
            dimension=CompatibilityDimension.CREATIVE_SYNERGY,
            score=round(final_score, 3),
            confidence=confidence,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.CREATIVE_SYNERGY],
            raw_metrics={
                'style_score': style_score,
                'process_score': process_score,
                'history_score': history_score
            }
        )
    
    async def _score_work_style(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score work style compatibility"""
        work_prefs_a = creator_a.work_preferences
        work_prefs_b = creator_b.work_preferences
        
        compatibility_factors = []
        
        # Work pace compatibility
        pace_a = work_prefs_a.get('work_pace', 0.5)  # 0=slow, 1=fast
        pace_b = work_prefs_b.get('work_pace', 0.5)
        pace_diff = abs(pace_a - pace_b)
        pace_score = 1.0 - pace_diff
        compatibility_factors.append(pace_score)
        
        # Meeting preferences
        meeting_pref_a = work_prefs_a.get('meeting_frequency', 0.5)  # 0=minimal, 1=frequent
        meeting_pref_b = work_prefs_b.get('meeting_frequency', 0.5)
        meeting_diff = abs(meeting_pref_a - meeting_pref_b)
        meeting_score = 1.0 - meeting_diff
        compatibility_factors.append(meeting_score)
        
        # Decision making style
        decision_a = work_prefs_a.get('decision_making', 0.5)  # 0=consensus, 1=decisive
        decision_b = work_prefs_b.get('decision_making', 0.5)
        decision_diff = abs(decision_a - decision_b)
        decision_score = 1.0 - decision_diff
        compatibility_factors.append(decision_score)
        
        # Flexibility
        flexibility_a = work_prefs_a.get('flexibility', 0.5)  # 0=rigid, 1=flexible
        flexibility_b = work_prefs_b.get('flexibility', 0.5)
        flexibility_score = (flexibility_a + flexibility_b) / 2  # Higher is better
        compatibility_factors.append(flexibility_score)
        
        # Work hour preferences
        schedule_a = creator_a.schedule_patterns
        schedule_b = creator_b.schedule_patterns
        
        preferred_hours_a = schedule_a.get('preferred_work_hours', [9, 17])  # Default 9-5
        preferred_hours_b = schedule_b.get('preferred_work_hours', [9, 17])
        
        # Calculate overlap in preferred hours
        start_overlap = max(preferred_hours_a[0], preferred_hours_b[0])
        end_overlap = min(preferred_hours_a[1], preferred_hours_b[1])
        overlap_hours = max(0, end_overlap - start_overlap)
        
        # Ideal overlap is 4-6 hours
        if 4 <= overlap_hours <= 6:
            schedule_score = 1.0
        elif overlap_hours >= 2:
            schedule_score = 0.7
        else:
            schedule_score = 0.3
        
        compatibility_factors.append(schedule_score)
        
        # Final work style score
        final_score = sum(compatibility_factors) / len(compatibility_factors)
        
        # Contributing factors
        contributing_factors = []
        if pace_score > 0.8:
            contributing_factors.append("Compatible work pace preferences")
        if meeting_score > 0.8:
            contributing_factors.append("Aligned meeting and communication preferences")
        if flexibility_score > 0.7:
            contributing_factors.append("Good flexibility and adaptability")
        if schedule_score > 0.7:
            contributing_factors.append(f"Overlapping work hours ({overlap_hours} hours)")
        
        # Improvement suggestions
        improvement_suggestions = []
        if pace_score < 0.6:
            improvement_suggestions.append("Discuss and establish mutually comfortable work pace")
        if meeting_score < 0.6:
            improvement_suggestions.append("Agree on communication frequency and meeting schedules")
        if schedule_score < 0.5:
            improvement_suggestions.append("Coordinate schedules for better collaboration windows")
        
        confidence = self._determine_confidence(final_score, len(contributing_factors))
        
        return DimensionScore(
            dimension=CompatibilityDimension.WORK_STYLE,
            score=round(final_score, 3),
            confidence=confidence,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.WORK_STYLE],
            raw_metrics={
                'pace_score': pace_score,
                'meeting_score': meeting_score,
                'decision_score': decision_score,
                'flexibility_score': flexibility_score,
                'schedule_score': schedule_score,
                'overlap_hours': overlap_hours
            }
        )
    
    async def _score_communication(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score communication compatibility"""
        comm_a = creator_a.communication_style
        comm_b = creator_b.communication_style
        
        communication_factors = []
        
        # Communication style alignment
        style_alignment = 0.0
        style_count = 0
        
        for style in ['directness', 'formality', 'detail_level', 'responsiveness']:
            if style in comm_a and style in comm_b:
                diff = abs(comm_a[style] - comm_b[style])
                alignment = 1.0 - diff
                style_alignment += alignment
                style_count += 1
        
        if style_count > 0:
            style_score = style_alignment / style_count
        else:
            style_score = 0.6
        
        communication_factors.append(style_score)
        
        # Preferred communication channels
        channels_a = creator_a.work_preferences.get('communication_channels', [])
        channels_b = creator_b.work_preferences.get('communication_channels', [])
        
        if channels_a and channels_b:
            common_channels = set(channels_a).intersection(set(channels_b))
            channel_score = len(common_channels) / max(len(set(channels_a).union(set(channels_b))), 1)
        else:
            channel_score = 0.5
        
        communication_factors.append(channel_score)
        
        # Response time compatibility
        response_time_a = creator_a.work_preferences.get('expected_response_time', 24)  # hours
        response_time_b = creator_b.work_preferences.get('expected_response_time', 24)
        
        # Both should have reasonable response expectations
        max_response_time = max(response_time_a, response_time_b)
        min_response_time = min(response_time_a, response_time_b)
        
        if max_response_time <= min_response_time * 2:  # Within 2x of each other
            response_score = 1.0
        else:
            response_score = 0.5
        
        communication_factors.append(response_score)
        
        # Feedback style compatibility
        feedback_history_a = creator_a.feedback_history
        feedback_history_b = creator_b.feedback_history
        
        if feedback_history_a and feedback_history_b:
            # Analyze feedback giving and receiving patterns
            avg_feedback_quality_a = sum(f.get('quality_rating', 3) for f in feedback_history_a) / len(feedback_history_a)
            avg_feedback_quality_b = sum(f.get('quality_rating', 3) for f in feedback_history_b) / len(feedback_history_b)
            
            feedback_score = (avg_feedback_quality_a + avg_feedback_quality_b) / 10  # Normalize to 0-1
        else:
            feedback_score = 0.6  # Default for new collaborators
        
        communication_factors.append(feedback_score)
        
        # Final communication score
        final_score = sum(communication_factors) / len(communication_factors)
        
        # Contributing factors
        contributing_factors = []
        if style_score > 0.8:
            contributing_factors.append("Well-aligned communication styles")
        if channel_score > 0.7:
            contributing_factors.append("Compatible communication channel preferences")
        if response_score > 0.8:
            contributing_factors.append("Compatible response time expectations")
        if feedback_score > 0.7:
            contributing_factors.append("Good feedback history and practices")
        
        # Improvement suggestions
        improvement_suggestions = []
        if style_score < 0.6:
            improvement_suggestions.append("Establish communication style preferences and expectations")
        if channel_score < 0.5:
            improvement_suggestions.append("Agree on primary communication channels and tools")
        if response_score < 0.7:
            improvement_suggestions.append("Set clear response time expectations")
        
        confidence = self._determine_confidence(final_score, len(contributing_factors))
        
        return DimensionScore(
            dimension=CompatibilityDimension.COMMUNICATION,
            score=round(final_score, 3),
            confidence=confidence,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.COMMUNICATION],
            raw_metrics={
                'style_score': style_score,
                'channel_score': channel_score,
                'response_score': response_score,
                'feedback_score': feedback_score
            }
        )
    
    async def _score_schedule_compatibility(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score schedule and timing compatibility"""
        schedule_a = creator_a.schedule_patterns
        schedule_b = creator_b.schedule_patterns
        
        compatibility_factors = []
        
        # Timezone compatibility
        tz_a = schedule_a.get('timezone', 'UTC')
        tz_b = schedule_b.get('timezone', 'UTC')
        
        # Simplified timezone difference calculation
        if tz_a == tz_b:
            timezone_score = 1.0
        else:
            # Assume different timezones have some compatibility issues
            timezone_score = 0.6
        
        compatibility_factors.append(timezone_score)
        
        # Available days overlap
        days_a = set(schedule_a.get('available_days', ['mon', 'tue', 'wed', 'thu', 'fri']))
        days_b = set(schedule_b.get('available_days', ['mon', 'tue', 'wed', 'thu', 'fri']))
        
        overlapping_days = days_a.intersection(days_b)
        total_unique_days = days_a.union(days_b)
        
        if total_unique_days:
            days_score = len(overlapping_days) / len(total_unique_days)
        else:
            days_score = 0.5
        
        compatibility_factors.append(days_score)
        
        # Working hours overlap (already calculated in work_style)
        preferred_hours_a = schedule_a.get('preferred_work_hours', [9, 17])
        preferred_hours_b = schedule_b.get('preferred_work_hours', [9, 17])
        
        start_overlap = max(preferred_hours_a[0], preferred_hours_b[0])
        end_overlap = min(preferred_hours_a[1], preferred_hours_b[1])
        overlap_hours = max(0, end_overlap - start_overlap)
        
        if overlap_hours >= 4:
            hours_score = 1.0
        elif overlap_hours >= 2:
            hours_score = 0.7
        else:
            hours_score = 0.3
        
        compatibility_factors.append(hours_score)
        
        # Availability consistency
        availability_a = schedule_a.get('consistency_rating', 0.7)  # How consistent is their schedule
        availability_b = schedule_b.get('consistency_rating', 0.7)
        
        # Both having consistent schedules is good
        consistency_score = (availability_a + availability_b) / 2
        compatibility_factors.append(consistency_score)
        
        # Final schedule score
        final_score = sum(compatibility_factors) / len(compatibility_factors)
        
        # Contributing factors
        contributing_factors = []
        if timezone_score > 0.8:
            contributing_factors.append("Compatible or same timezone")
        if days_score > 0.7:
            contributing_factors.append(f"Good day availability overlap ({len(overlapping_days)} common days)")
        if hours_score > 0.7:
            contributing_factors.append(f"Sufficient working hours overlap ({overlap_hours} hours)")
        if consistency_score > 0.7:
            contributing_factors.append("Both creators have consistent schedules")
        
        # Improvement suggestions
        improvement_suggestions = []
        if timezone_score < 0.7:
            improvement_suggestions.append("Plan for timezone differences in meeting scheduling")
        if days_score < 0.5:
            improvement_suggestions.append("Coordinate to find more overlapping available days")
        if hours_score < 0.5:
            improvement_suggestions.append("Establish dedicated collaboration time windows")
        
        confidence = self._determine_confidence(final_score, len(contributing_factors))
        
        return DimensionScore(
            dimension=CompatibilityDimension.SCHEDULE_COMPATIBILITY,
            score=round(final_score, 3),
            confidence=confidence,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.SCHEDULE_COMPATIBILITY],
            raw_metrics={
                'timezone_score': timezone_score,
                'days_score': days_score,
                'hours_score': hours_score,
                'consistency_score': consistency_score,
                'overlapping_days': list(overlapping_days),
                'overlap_hours': overlap_hours
            }
        )
    
    async def _score_technical_compatibility(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score technical setup and capability compatibility"""
        tech_a = creator_a.technical_setup
        tech_b = creator_b.technical_setup
        
        compatibility_factors = []
        
        # Software compatibility
        software_a = set(tech_a.get('software', []))
        software_b = set(tech_b.get('software', []))
        
        if software_a and software_b:
            common_software = software_a.intersection(software_b)
            total_software = software_a.union(software_b)
            software_score = len(common_software) / len(total_software)
        else:
            software_score = 0.5
        
        compatibility_factors.append(software_score)
        
        # File format compatibility
        formats_a = set(tech_a.get('supported_formats', []))
        formats_b = set(tech_b.get('supported_formats', []))
        
        if formats_a and formats_b:
            common_formats = formats_a.intersection(formats_b)
            if common_formats:
                format_score = 1.0
            else:
                format_score = 0.3  # No common formats is problematic
        else:
            format_score = 0.6
        
        compatibility_factors.append(format_score)
        
        # Quality level compatibility
        quality_level_a = tech_a.get('quality_level', 'standard')  # basic, standard, professional
        quality_level_b = tech_b.get('quality_level', 'standard')
        
        quality_levels = {'basic': 1, 'standard': 2, 'professional': 3}
        level_a = quality_levels.get(quality_level_a, 2)
        level_b = quality_levels.get(quality_level_b, 2)
        
        level_diff = abs(level_a - level_b)
        if level_diff == 0:
            quality_compatibility = 1.0
        elif level_diff == 1:
            quality_compatibility = 0.7
        else:
            quality_compatibility = 0.4
        
        compatibility_factors.append(quality_compatibility)
        
        # Internet/connectivity compatibility
        connectivity_a = tech_a.get('connectivity_quality', 0.8)  # 0-1 scale
        connectivity_b = tech_b.get('connectivity_quality', 0.8)
        
        # Both need good connectivity for collaboration
        min_connectivity = min(connectivity_a, connectivity_b)
        connectivity_score = min_connectivity
        
        compatibility_factors.append(connectivity_score)
        
        # Final technical score
        final_score = sum(compatibility_factors) / len(compatibility_factors)
        
        # Contributing factors
        contributing_factors = []
        if software_score > 0.6:
            contributing_factors.append(f"Good software compatibility ({len(software_a.intersection(software_b))} common tools)")
        if format_score > 0.8:
            contributing_factors.append("Compatible file formats")
        if quality_compatibility > 0.8:
            contributing_factors.append("Matching technical quality levels")
        if connectivity_score > 0.8:
            contributing_factors.append("Reliable internet connectivity for both creators")
        
        # Improvement suggestions
        improvement_suggestions = []
        if software_score < 0.4:
            improvement_suggestions.append("Consider adopting common software tools for collaboration")
        if format_score < 0.5:
            improvement_suggestions.append("Establish compatible file formats for sharing work")
        if quality_compatibility < 0.6:
            improvement_suggestions.append("Align on technical quality standards and requirements")
        
        confidence = self._determine_confidence(final_score, len(contributing_factors))
        
        return DimensionScore(
            dimension=CompatibilityDimension.TECHNICAL_COMPATIBILITY,
            score=round(final_score, 3),
            confidence=confidence,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.TECHNICAL_COMPATIBILITY],
            raw_metrics={
                'software_score': software_score,
                'format_score': format_score,
                'quality_compatibility': quality_compatibility,
                'connectivity_score': connectivity_score,
                'common_software': list(software_a.intersection(software_b)) if software_a and software_b else [],
                'common_formats': list(formats_a.intersection(formats_b)) if formats_a and formats_b else []
            }
        )
    
    async def _score_cultural_fit(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score cultural fit and values alignment"""
        cultural_a = creator_a.cultural_attributes
        cultural_b = creator_b.cultural_attributes
        
        # Simplified cultural compatibility scoring
        # In a real implementation, this would be more sophisticated
        
        compatibility_factors = []
        
        # Language compatibility
        languages_a = set(cultural_a.get('languages', ['en']))
        languages_b = set(cultural_b.get('languages', ['en']))
        
        common_languages = languages_a.intersection(languages_b)
        if common_languages:
            language_score = 1.0
        else:
            language_score = 0.3  # Language barrier
        
        compatibility_factors.append(language_score)
        
        # Cultural values alignment (simplified)
        values_a = cultural_a.get('values', {})
        values_b = cultural_b.get('values', {})
        
        if values_a and values_b:
            value_alignment = 0.0
            value_count = 0
            
            for value in ['professionalism', 'creativity', 'collaboration', 'innovation']:
                if value in values_a and value in values_b:
                    diff = abs(values_a[value] - values_b[value])
                    value_alignment += 1.0 - diff
                    value_count += 1
            
            if value_count > 0:
                values_score = value_alignment / value_count
            else:
                values_score = 0.7
        else:
            values_score = 0.7  # Default moderate alignment
        
        compatibility_factors.append(values_score)
        
        # Work culture compatibility
        work_culture_a = cultural_a.get('work_culture', 'balanced')  # relaxed, balanced, intense
        work_culture_b = cultural_b.get('work_culture', 'balanced')
        
        culture_compatibility = {
            ('relaxed', 'relaxed'): 1.0,
            ('balanced', 'balanced'): 1.0,
            ('intense', 'intense'): 1.0,
            ('relaxed', 'balanced'): 0.8,
            ('balanced', 'intense'): 0.8,
            ('relaxed', 'intense'): 0.4
        }
        
        culture_key = tuple(sorted([work_culture_a, work_culture_b]))
        culture_score = culture_compatibility.get(culture_key, 0.6)
        
        compatibility_factors.append(culture_score)
        
        # Final cultural score
        final_score = sum(compatibility_factors) / len(compatibility_factors)
        
        # Contributing factors
        contributing_factors = []
        if language_score > 0.8:
            contributing_factors.append(f"Shared languages: {', '.join(common_languages)}")
        if values_score > 0.8:
            contributing_factors.append("Well-aligned cultural values")
        if culture_score > 0.8:
            contributing_factors.append("Compatible work culture preferences")
        
        # Improvement suggestions
        improvement_suggestions = []
        if language_score < 0.5:
            improvement_suggestions.append("Consider using translation tools or common language")
        if values_score < 0.6:
            improvement_suggestions.append("Discuss and align on core values and principles")
        
        confidence = self._determine_confidence(final_score, len(contributing_factors))
        
        return DimensionScore(
            dimension=CompatibilityDimension.CULTURAL_FIT,
            score=round(final_score, 3),
            confidence=confidence,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.CULTURAL_FIT],
            raw_metrics={
                'language_score': language_score,
                'values_score': values_score,
                'culture_score': culture_score,
                'common_languages': list(common_languages)
            }
        )
    
    async def _score_business_alignment(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score business goals and approach alignment"""
        business_a = creator_a.business_metrics
        business_b = creator_b.business_metrics
        
        compatibility_factors = []
        
        # Career stage compatibility
        stage_a = business_a.get('career_stage', 'intermediate')  # beginner, intermediate, advanced
        stage_b = business_b.get('career_stage', 'intermediate')
        
        stages = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
        stage_diff = abs(stages.get(stage_a, 2) - stages.get(stage_b, 2))
        
        if stage_diff == 0:
            stage_score = 1.0
        elif stage_diff == 1:
            stage_score = 0.8
        else:
            stage_score = 0.5
        
        compatibility_factors.append(stage_score)
        
        # Business goals alignment
        goals_a = set(business_a.get('goals', []))
        goals_b = set(business_b.get('goals', []))
        
        if goals_a and goals_b:
            common_goals = goals_a.intersection(goals_b)
            total_goals = goals_a.union(goals_b)
            goals_score = len(common_goals) / len(total_goals)
        else:
            goals_score = 0.6
        
        compatibility_factors.append(goals_score)
        
        # Monetization approach compatibility
        monetization_a = business_a.get('monetization_focus', 0.5)  # 0=passion, 1=profit
        monetization_b = business_b.get('monetization_focus', 0.5)
        
        monetization_diff = abs(monetization_a - monetization_b)
        monetization_score = 1.0 - monetization_diff
        
        compatibility_factors.append(monetization_score)
        
        # Final business score
        final_score = sum(compatibility_factors) / len(compatibility_factors)
        
        # Contributing factors
        contributing_factors = []
        if stage_score > 0.8:
            contributing_factors.append("Compatible career development stages")
        if goals_score > 0.6:
            contributing_factors.append(f"Shared business goals ({len(goals_a.intersection(goals_b))} common)")
        if monetization_score > 0.8:
            contributing_factors.append("Aligned monetization and business approach")
        
        # Improvement suggestions
        improvement_suggestions = []
        if goals_score < 0.4:
            improvement_suggestions.append("Discuss and find common business objectives")
        if monetization_score < 0.6:
            improvement_suggestions.append("Align on collaboration monetization approach")
        
        confidence = self._determine_confidence(final_score, len(contributing_factors))
        
        return DimensionScore(
            dimension=CompatibilityDimension.BUSINESS_ALIGNMENT,
            score=round(final_score, 3),
            confidence=confidence,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.BUSINESS_ALIGNMENT],
            raw_metrics={
                'stage_score': stage_score,
                'goals_score': goals_score,
                'monetization_score': monetization_score
            }
        )
    
    async def _score_reputation_match(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score reputation and credibility compatibility"""
        # Get reputation metrics
        rep_a = creator_a.business_metrics.get('reputation_score', 3.5)
        rep_b = creator_b.business_metrics.get('reputation_score', 3.5)
        
        # Reputation should be reasonably matched
        rep_diff = abs(rep_a - rep_b)
        
        if rep_diff <= 0.5:
            reputation_score = 1.0
        elif rep_diff <= 1.0:
            reputation_score = 0.7
        else:
            reputation_score = 0.4
        
        # Both should have decent reputations
        min_reputation = min(rep_a, rep_b)
        if min_reputation < 2.5:
            reputation_score *= 0.7  # Penalty for low reputation
        
        # Contributing factors
        contributing_factors = []
        if reputation_score > 0.8:
            contributing_factors.append(f"Well-matched reputation levels ({rep_a:.1f} and {rep_b:.1f})")
        if min_reputation > 4.0:
            contributing_factors.append("Both creators have excellent reputations")
        
        # Improvement suggestions
        improvement_suggestions = []
        if reputation_score < 0.6:
            improvement_suggestions.append("Consider building reputation through smaller collaborations first")
        
        confidence = self._determine_confidence(reputation_score, len(contributing_factors))
        
        return DimensionScore(
            dimension=CompatibilityDimension.REPUTATION_MATCH,
            score=round(reputation_score, 3),
            confidence=confidence,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.REPUTATION_MATCH],
            raw_metrics={
                'reputation_a': rep_a,
                'reputation_b': rep_b,
                'reputation_diff': rep_diff
            }
        )
    
    async def _score_audience_overlap(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> DimensionScore:
        """Score audience overlap and cross-promotion potential"""
        # Get audience metrics
        audience_a = creator_a.business_metrics.get('audience_size', 1000)
        audience_b = creator_b.business_metrics.get('audience_size', 1000)
        
        # Some overlap is good, too much might cannibalize
        # This is a simplified calculation
        size_ratio = min(audience_a, audience_b) / max(audience_a, audience_b)
        
        if 0.3 <= size_ratio <= 0.8:  # Good complementary sizes
            size_score = 1.0
        elif 0.1 <= size_ratio <= 1.0:  # Acceptable range
            size_score = 0.7
        else:  # Too different
            size_score = 0.4
        
        # Engagement rate factor
        engagement_a = creator_a.business_metrics.get('engagement_rate', 0.05)
        engagement_b = creator_b.business_metrics.get('engagement_rate', 0.05)
        
        avg_engagement = (engagement_a + engagement_b) / 2
        engagement_score = min(1.0, avg_engagement / 0.08)  # 8% is excellent
        
        # Combined audience score
        audience_score = (size_score * 0.7 + engagement_score * 0.3)
        
        # Contributing factors
        contributing_factors = []
        if size_score > 0.8:
            contributing_factors.append("Complementary audience sizes for cross-promotion")
        if engagement_score > 0.7:
            contributing_factors.append("Good audience engagement rates")
        
        # Improvement suggestions
        improvement_suggestions = []
        if size_score < 0.5:
            improvement_suggestions.append("Consider targeting different audience segments")
        
        confidence = self._determine_confidence(audience_score, len(contributing_factors))
        
        return DimensionScore(
            dimension=CompatibilityDimension.AUDIENCE_OVERLAP,
            score=round(audience_score, 3),
            confidence=confidence,
            contributing_factors=contributing_factors,
            improvement_suggestions=improvement_suggestions,
            weight=self.dimension_weights[CompatibilityDimension.AUDIENCE_OVERLAP],
            raw_metrics={
                'audience_a': audience_a,
                'audience_b': audience_b,
                'size_ratio': size_ratio,
                'engagement_a': engagement_a,
                'engagement_b': engagement_b
            }
        )
    
    def _determine_confidence(self, score: float, contributing_factors_count: int) -> ScoreConfidence:
        """Determine confidence level based on score and factors"""
        # Base confidence on score
        if score >= 0.8:
            base_confidence = ScoreConfidence.HIGH
        elif score >= 0.6:
            base_confidence = ScoreConfidence.MEDIUM
        elif score >= 0.4:
            base_confidence = ScoreConfidence.LOW
        else:
            base_confidence = ScoreConfidence.VERY_LOW
        
        # Adjust based on number of contributing factors
        if contributing_factors_count >= 3 and base_confidence == ScoreConfidence.HIGH:
            return ScoreConfidence.VERY_HIGH
        elif contributing_factors_count == 0 and base_confidence != ScoreConfidence.VERY_LOW:
            # Reduce confidence if no supporting factors
            confidence_order = [ScoreConfidence.VERY_LOW, ScoreConfidence.LOW, 
                              ScoreConfidence.MEDIUM, ScoreConfidence.HIGH, ScoreConfidence.VERY_HIGH]
            current_index = confidence_order.index(base_confidence)
            return confidence_order[max(0, current_index - 1)]
        
        return base_confidence
    
    async def _calculate_overall_score(self, dimension_scores: List[DimensionScore]) -> float:
        """Calculate weighted overall compatibility score"""
        weighted_sum = sum(score.score * score.weight for score in dimension_scores)
        total_weight = sum(score.weight for score in dimension_scores)
        
        return round(weighted_sum / total_weight, 3)
    
    async def _calculate_overall_confidence(self, dimension_scores: List[DimensionScore]) -> ScoreConfidence:
        """Calculate overall confidence based on dimension confidences"""
        confidence_values = {
            ScoreConfidence.VERY_LOW: 1,
            ScoreConfidence.LOW: 2,
            ScoreConfidence.MEDIUM: 3,
            ScoreConfidence.HIGH: 4,
            ScoreConfidence.VERY_HIGH: 5
        }
        
        # Weight confidence by dimension weights
        weighted_confidence = sum(
            confidence_values[score.confidence] * score.weight 
            for score in dimension_scores
        )
        total_weight = sum(score.weight for score in dimension_scores)
        
        avg_confidence = weighted_confidence / total_weight
        
        # Convert back to confidence level
        if avg_confidence >= 4.5:
            return ScoreConfidence.VERY_HIGH
        elif avg_confidence >= 3.5:
            return ScoreConfidence.HIGH
        elif avg_confidence >= 2.5:
            return ScoreConfidence.MEDIUM
        elif avg_confidence >= 1.5:
            return ScoreConfidence.LOW
        else:
            return ScoreConfidence.VERY_LOW
    
    async def _identify_strength_areas(self, dimension_scores: List[DimensionScore]) -> List[str]:
        """Identify top strength areas from dimension scores"""
        # Sort by score and get top performers
        top_dimensions = sorted(dimension_scores, key=lambda x: x.score, reverse=True)[:3]
        
        strengths = []
        for dim in top_dimensions:
            if dim.score > 0.7:
                strengths.append(f"{dim.dimension.value.replace('_', ' ').title()}: {dim.score:.2f}")
        
        return strengths
    
    async def _identify_concern_areas(self, dimension_scores: List[DimensionScore]) -> List[str]:
        """Identify areas of concern from dimension scores"""
        concerns = []
        
        for dim in dimension_scores:
            if dim.score < 0.5:
                concerns.append(f"{dim.dimension.value.replace('_', ' ').title()}: {dim.score:.2f}")
        
        # Sort by severity (lowest scores first)
        return sorted(concerns)
    
    async def _generate_collaboration_recommendations(
        self,
        dimension_scores: List[DimensionScore],
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> List[str]:
        """Generate specific collaboration recommendations"""
        recommendations = []
        
        # Collect improvement suggestions from all dimensions
        for dim in dimension_scores:
            if dim.score < 0.7 and dim.improvement_suggestions:
                recommendations.extend(dim.improvement_suggestions)
        
        # Add general recommendations based on overall compatibility
        overall_score = await self._calculate_overall_score(dimension_scores)
        
        if overall_score > 0.8:
            recommendations.append("Excellent compatibility - proceed with confidence")
        elif overall_score > 0.6:
            recommendations.append("Good compatibility - address minor concerns before proceeding")
        else:
            recommendations.append("Consider addressing major compatibility issues before collaboration")
        
        return recommendations[:8]  # Limit to 8 recommendations
    
    async def _identify_risk_factors(
        self,
        dimension_scores: List[DimensionScore],
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> List[str]:
        """Identify potential risk factors for the collaboration"""
        risks = []
        
        # Analyze low-scoring dimensions for risks
        for dim in dimension_scores:
            if dim.score < 0.4:
                risks.append(f"Low {dim.dimension.value.replace('_', ' ')}: {dim.score:.2f}")
        
        # Add specific risk patterns
        schedule_score = next((d.score for d in dimension_scores 
                             if d.dimension == CompatibilityDimension.SCHEDULE_COMPATIBILITY), 0.5)
        if schedule_score < 0.5:
            risks.append("Schedule conflicts may impact project timeline")
        
        communication_score = next((d.score for d in dimension_scores 
                                  if d.dimension == CompatibilityDimension.COMMUNICATION), 0.5)
        if communication_score < 0.5:
            risks.append("Communication issues may lead to misunderstandings")
        
        return risks[:6]  # Limit to 6 risks
    
    async def _identify_success_predictors(
        self,
        dimension_scores: List[DimensionScore],
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> List[str]:
        """Identify factors that predict collaboration success"""
        predictors = []
        
        # High-scoring dimensions indicate success factors
        for dim in dimension_scores:
            if dim.score > 0.8:
                predictors.append(f"Strong {dim.dimension.value.replace('_', ' ')}")
        
        # Add specific success patterns
        if len([d for d in dimension_scores if d.score > 0.7]) >= 6:
            predictors.append("Multiple strong compatibility dimensions")
        
        # Experience factor
        history_a = len(creator_a.collaboration_history)
        history_b = len(creator_b.collaboration_history)
        if history_a > 3 and history_b > 3:
            predictors.append("Both creators have extensive collaboration experience")
        
        return predictors[:6]  # Limit to 6 predictors
    
    async def _recommend_collaboration_types(
        self,
        dimension_scores: List[DimensionScore],
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> List[str]:
        """Recommend optimal collaboration types based on compatibility"""
        # Get key dimension scores
        creative_score = next((d.score for d in dimension_scores 
                             if d.dimension == CompatibilityDimension.CREATIVE_SYNERGY), 0.5)
        technical_score = next((d.score for d in dimension_scores 
                              if d.dimension == CompatibilityDimension.TECHNICAL_COMPATIBILITY), 0.5)
        schedule_score = next((d.score for d in dimension_scores 
                             if d.dimension == CompatibilityDimension.SCHEDULE_COMPATIBILITY), 0.5)
        
        recommendations = []
        
        if creative_score > 0.8:
            recommendations.append("Joint creative projects")
        
        if technical_score > 0.7:
            recommendations.append("Technical collaboration and skill sharing")
        
        if schedule_score > 0.7:
            recommendations.append("Real-time collaborative sessions")
        else:
            recommendations.append("Asynchronous collaboration projects")
        
        # Default recommendations
        if not recommendations:
            recommendations.extend(["Cross-promotion", "Content exchange", "Mentorship arrangement"])
        
        return recommendations[:4]
    
    async def _generate_timeline_recommendations(
        self,
        dimension_scores: List[DimensionScore],
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> str:
        """Generate timeline recommendations for the collaboration"""
        overall_score = await self._calculate_overall_score(dimension_scores)
        
        if overall_score > 0.8:
            return "Can proceed immediately with full collaboration"
        elif overall_score > 0.6:
            return "Start with 2-week trial period, then full collaboration"
        elif overall_score > 0.4:
            return "Begin with limited scope project over 4-6 weeks"
        else:
            return "Consider 1-month preparation period to address compatibility issues"
    
    async def _analyze_budget_implications(
        self,
        dimension_scores: List[DimensionScore],
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> Dict[str, Any]:
        """Analyze budget implications based on compatibility"""
        overall_score = await self._calculate_overall_score(dimension_scores)
        
        # Base collaboration cost factor
        if overall_score > 0.8:
            cost_factor = 1.0  # Smooth collaboration
        elif overall_score > 0.6:
            cost_factor = 1.2  # Some additional coordination costs
        else:
            cost_factor = 1.5  # Higher costs due to compatibility issues
        
        return {
            'cost_factor': cost_factor,
            'recommendation': f"Budget {int((cost_factor - 1) * 100)}% extra for coordination overhead",
            'efficiency_rating': 'high' if cost_factor <= 1.1 else 'medium' if cost_factor <= 1.3 else 'low'
        }


# Export main class
__all__ = ['CompatibilityScorer', 'CompatibilityReport', 'DimensionScore', 'CreatorCompatibilityProfile', 
           'CompatibilityDimension', 'ScoreConfidence']