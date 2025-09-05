"""Temporal Analyzer Module - Advanced Time Pattern and Schedule Analysis
=====================================================================

Sophisticated temporal analysis system for creator collaboration optimization based on
time patterns, schedule compatibility, content timing, and temporal synchronization
for maximum collaboration effectiveness.

This module implements:
- Creator schedule pattern analysis and compatibility
- Optimal collaboration timing identification
- Content release timing optimization
- Temporal workload distribution analysis
- Availability prediction and planning

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta, time
from enum import Enum
import calendar
import pytz
import numpy as np
import pandas as pd
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)


class SchedulePattern(Enum):
    """Types of schedule patterns"""
    MORNING_FOCUSED = "morning_focused"      # Peak 6-12
    AFTERNOON_FOCUSED = "afternoon_focused"  # Peak 12-18
    EVENING_FOCUSED = "evening_focused"      # Peak 18-24
    NIGHT_FOCUSED = "night_focused"          # Peak 0-6
    SPLIT_SCHEDULE = "split_schedule"        # Multiple peaks
    FLEXIBLE = "flexible"                    # No clear pattern
    WEEKEND_WARRIOR = "weekend_warrior"      # Weekend focused
    BUSINESS_HOURS = "business_hours"        # 9-17 focused


class ActivityType(Enum):
    """Types of creator activities"""
    CONTENT_CREATION = "content_creation"
    EDITING = "editing"
    SOCIAL_MEDIA = "social_media"
    MEETINGS = "meetings"
    COLLABORATION = "collaboration"
    RESEARCH = "research"
    ADMIN = "admin"
    PERSONAL_TIME = "personal_time"


class CompatibilityLevel(Enum):
    """Schedule compatibility levels"""
    EXCELLENT = "excellent"    # 80%+ overlap
    GOOD = "good"             # 60-79% overlap
    MODERATE = "moderate"     # 40-59% overlap
    LIMITED = "limited"       # 20-39% overlap
    POOR = "poor"             # <20% overlap


@dataclass
class TimeSlot:
    """Individual time slot with activity information"""
    start_time: datetime
    end_time: datetime
    activity_type: ActivityType
    productivity_level: float  # 0-1 scale
    availability_for_collaboration: float  # 0-1 scale
    energy_level: float  # 0-1 scale
    focus_quality: float  # 0-1 scale
    interruption_tolerance: float  # 0-1 scale
    timezone: str
    recurring_pattern: Optional[str] = None  # daily, weekly, etc.


@dataclass
class SchedulePattern:
    """Creator's schedule pattern analysis"""
    creator_id: str
    primary_pattern: SchedulePattern
    active_hours: List[Tuple[int, int]]  # Hour ranges when most active
    peak_productivity_times: List[Tuple[int, int]]  # Best productivity windows
    collaboration_windows: List[TimeSlot]  # Available for collaboration
    weekly_pattern: Dict[str, List[TimeSlot]]  # Day-wise patterns
    monthly_variations: Dict[str, float]  # Month-wise availability changes
    seasonal_adjustments: Dict[str, float]  # Seasonal pattern changes
    timezone: str
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AvailabilityMatch:
    """Availability match between creators"""
    creator_ids: List[str]
    overlapping_slots: List[TimeSlot]
    compatibility_score: float
    optimal_meeting_times: List[Dict[str, Any]]
    collaboration_duration_options: List[int]  # Possible durations in minutes
    frequency_potential: Dict[str, int]  # daily, weekly, monthly possibilities
    energy_alignment: float  # How well energy levels align
    productivity_alignment: float  # How well productivity peaks align


@dataclass
class TemporalPatterns:
    """Comprehensive temporal patterns analysis"""
    individual_patterns: List[SchedulePattern]
    group_compatibility: CompatibilityLevel
    optimal_collaboration_schedule: Dict[str, Any]
    temporal_advantages: List[str]
    temporal_challenges: List[str]
    recommended_meeting_cadence: Dict[str, Any]
    content_timing_optimization: Dict[str, Any]
    workload_distribution: Dict[str, Any]
    seasonal_considerations: List[str]


@dataclass
class TimeAnalysis:
    """Detailed time analysis for collaboration optimization"""
    analysis_period: Tuple[datetime, datetime]
    creator_time_profiles: List[SchedulePattern]
    availability_matches: List[AvailabilityMatch]
    temporal_synergies: List[Dict[str, Any]]
    optimal_project_timeline: Dict[str, Any]
    risk_factors: List[str]
    mitigation_strategies: List[str]
    confidence_score: float


@dataclass
class ScheduleCompatibility:
    """Overall schedule compatibility assessment"""
    creators: List[str]
    overall_compatibility: CompatibilityLevel
    best_collaboration_windows: List[Dict[str, Any]]
    meeting_frequency_recommendations: Dict[str, int]
    temporal_workflow_optimization: Dict[str, Any]
    schedule_conflict_analysis: Dict[str, Any]
    productivity_optimization: Dict[str, Any]
    long_term_sustainability: Dict[str, Any]


class TemporalAnalyzer:
    """Advanced temporal analysis engine for creator collaboration"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the temporal analyzer"""
        self.config = config or {}
        self.timezone_cache = {}
        self.pattern_cache = {}
        self.productivity_models = {}
        
        logger.info("⏰ Temporal Analyzer initialized")
    
    async def analyze_schedule_compatibility(
        self,
        creator_schedules: List[Dict[str, Any]]
    ) -> ScheduleCompatibility:
        """Analyze comprehensive schedule compatibility between creators"""
        try:
            logger.info(f"⏰ Analyzing schedule compatibility for {len(creator_schedules)} creators")
            
            if len(creator_schedules) < 2:
                raise ValueError("Need at least 2 creator schedules for compatibility analysis")
            
            # Build schedule patterns for each creator
            schedule_patterns = []
            for schedule_data in creator_schedules:
                pattern = await self._build_schedule_pattern(schedule_data)
                schedule_patterns.append(pattern)
            
            # Analyze availability matches
            availability_matches = await self._find_availability_matches(schedule_patterns)
            
            # Calculate overall compatibility
            overall_compatibility = await self._calculate_overall_compatibility(availability_matches)
            
            # Find best collaboration windows
            best_windows = await self._identify_best_collaboration_windows(
                schedule_patterns, availability_matches
            )
            
            # Generate meeting frequency recommendations
            frequency_recommendations = await self._recommend_meeting_frequency(
                availability_matches, schedule_patterns
            )
            
            # Optimize temporal workflow
            workflow_optimization = await self._optimize_temporal_workflow(schedule_patterns)
            
            # Analyze schedule conflicts
            conflict_analysis = await self._analyze_schedule_conflicts(schedule_patterns)
            
            # Optimize productivity
            productivity_optimization = await self._optimize_productivity_alignment(schedule_patterns)
            
            # Assess long-term sustainability
            sustainability = await self._assess_long_term_sustainability(schedule_patterns)
            
            compatibility = ScheduleCompatibility(
                creators=[pattern.creator_id for pattern in schedule_patterns],
                overall_compatibility=overall_compatibility,
                best_collaboration_windows=best_windows,
                meeting_frequency_recommendations=frequency_recommendations,
                temporal_workflow_optimization=workflow_optimization,
                schedule_conflict_analysis=conflict_analysis,
                productivity_optimization=productivity_optimization,
                long_term_sustainability=sustainability
            )
            
            logger.info(f"✅ Schedule compatibility analysis completed: {overall_compatibility.value}")
            return compatibility
            
        except Exception as e:
            logger.error(f"❌ Error in schedule compatibility analysis: {e}")
            raise
    
    async def _build_schedule_pattern(self, schedule_data: Dict[str, Any]) -> SchedulePattern:
        """Build schedule pattern from creator data"""
        creator_id = schedule_data['creator_id']
        timezone_str = schedule_data.get('timezone', 'UTC')
        
        # Extract time slots from data
        time_slots = []
        raw_slots = schedule_data.get('time_slots', [])
        
        for slot_data in raw_slots:
            slot = TimeSlot(
                start_time=datetime.fromisoformat(slot_data['start_time']),
                end_time=datetime.fromisoformat(slot_data['end_time']),
                activity_type=ActivityType(slot_data.get('activity_type', 'content_creation')),
                productivity_level=slot_data.get('productivity_level', 0.7),
                availability_for_collaboration=slot_data.get('availability_for_collaboration', 0.5),
                energy_level=slot_data.get('energy_level', 0.7),
                focus_quality=slot_data.get('focus_quality', 0.7),
                interruption_tolerance=slot_data.get('interruption_tolerance', 0.5),
                timezone=timezone_str
            )
            time_slots.append(slot)
        
        # Analyze patterns
        primary_pattern = await self._identify_primary_pattern(time_slots)
        active_hours = await self._calculate_active_hours(time_slots)
        peak_productivity = await self._identify_peak_productivity_times(time_slots)
        collaboration_windows = await self._extract_collaboration_windows(time_slots)
        weekly_pattern = await self._analyze_weekly_pattern(time_slots)
        monthly_variations = await self._calculate_monthly_variations(schedule_data)
        seasonal_adjustments = await self._calculate_seasonal_adjustments(schedule_data)
        
        return SchedulePattern(
            creator_id=creator_id,
            primary_pattern=primary_pattern,
            active_hours=active_hours,
            peak_productivity_times=peak_productivity,
            collaboration_windows=collaboration_windows,
            weekly_pattern=weekly_pattern,
            monthly_variations=monthly_variations,
            seasonal_adjustments=seasonal_adjustments,
            timezone=timezone_str
        )
    
    async def _identify_primary_pattern(self, time_slots: List[TimeSlot]) -> SchedulePattern:
        """Identify the primary schedule pattern"""
        if not time_slots:
            return SchedulePattern.FLEXIBLE
        
        # Analyze activity distribution by hour
        hourly_activity = defaultdict(float)
        hourly_productivity = defaultdict(list)
        
        for slot in time_slots:
            start_hour = slot.start_time.hour
            end_hour = slot.end_time.hour
            
            # Handle slots that cross day boundary
            if end_hour < start_hour:
                end_hour += 24
            
            duration = end_hour - start_hour
            for hour in range(start_hour, end_hour):
                actual_hour = hour % 24
                hourly_activity[actual_hour] += duration
                hourly_productivity[actual_hour].append(slot.productivity_level)
        
        # Find peak activity periods
        max_activity = max(hourly_activity.values()) if hourly_activity else 0
        peak_hours = [
            hour for hour, activity in hourly_activity.items()
            if activity >= max_activity * 0.7
        ]
        
        if not peak_hours:
            return SchedulePattern.FLEXIBLE
        
        # Determine pattern based on peak hours
        if any(6 <= hour <= 12 for hour in peak_hours):
            if any(18 <= hour <= 23 for hour in peak_hours):
                return SchedulePattern.SPLIT_SCHEDULE
            return SchedulePattern.MORNING_FOCUSED
        elif any(12 <= hour <= 18 for hour in peak_hours):
            return SchedulePattern.AFTERNOON_FOCUSED
        elif any(18 <= hour <= 23 for hour in peak_hours):
            return SchedulePattern.EVENING_FOCUSED
        elif any(0 <= hour <= 6 for hour in peak_hours):
            return SchedulePattern.NIGHT_FOCUSED
        
        # Check for business hours pattern
        business_hours = set(range(9, 17))
        if set(peak_hours).issubset(business_hours):
            return SchedulePattern.BUSINESS_HOURS
        
        return SchedulePattern.FLEXIBLE
    
    async def _calculate_active_hours(self, time_slots: List[TimeSlot]) -> List[Tuple[int, int]]:
        """Calculate active hour ranges"""
        if not time_slots:
            return []
        
        # Get all active hours
        active_hours = set()
        for slot in time_slots:
            start_hour = slot.start_time.hour
            end_hour = slot.end_time.hour
            
            if end_hour < start_hour:  # Crosses midnight
                for hour in range(start_hour, 24):
                    active_hours.add(hour)
                for hour in range(0, end_hour):
                    active_hours.add(hour)
            else:
                for hour in range(start_hour, end_hour):
                    active_hours.add(hour)
        
        # Convert to ranges
        sorted_hours = sorted(active_hours)
        ranges = []
        start = sorted_hours[0]
        prev = start
        
        for hour in sorted_hours[1:]:
            if hour != prev + 1:  # Gap found
                ranges.append((start, prev + 1))
                start = hour
            prev = hour
        
        ranges.append((start, prev + 1))
        return ranges
    
    async def _identify_peak_productivity_times(self, time_slots: List[TimeSlot]) -> List[Tuple[int, int]]:
        """Identify peak productivity time windows"""
        if not time_slots:
            return []
        
        # Calculate average productivity by hour
        hourly_productivity = defaultdict(list)
        
        for slot in time_slots:
            start_hour = slot.start_time.hour
            end_hour = slot.end_time.hour
            
            if end_hour < start_hour:
                end_hour += 24
            
            for hour in range(start_hour, end_hour):
                actual_hour = hour % 24
                hourly_productivity[actual_hour].append(slot.productivity_level)
        
        # Calculate average productivity per hour
        avg_productivity = {}
        for hour, levels in hourly_productivity.items():
            avg_productivity[hour] = statistics.mean(levels)
        
        if not avg_productivity:
            return []
        
        # Find peak hours (top 75% productivity)
        max_productivity = max(avg_productivity.values())
        threshold = max_productivity * 0.75
        
        peak_hours = [
            hour for hour, productivity in avg_productivity.items()
            if productivity >= threshold
        ]
        
        # Convert to ranges
        peak_hours.sort()
        ranges = []
        if peak_hours:
            start = peak_hours[0]
            prev = start
            
            for hour in peak_hours[1:]:
                if hour != prev + 1:
                    ranges.append((start, prev + 1))
                    start = hour
                prev = hour
            
            ranges.append((start, prev + 1))
        
        return ranges
    
    async def _extract_collaboration_windows(self, time_slots: List[TimeSlot]) -> List[TimeSlot]:
        """Extract windows available for collaboration"""
        collaboration_slots = []
        
        for slot in time_slots:
            # Consider slots with high collaboration availability
            if slot.availability_for_collaboration >= 0.6:
                collaboration_slots.append(slot)
        
        return collaboration_slots
    
    async def _analyze_weekly_pattern(self, time_slots: List[TimeSlot]) -> Dict[str, List[TimeSlot]]:
        """Analyze weekly patterns"""
        weekly_pattern = {
            'monday': [],
            'tuesday': [],
            'wednesday': [],
            'thursday': [],
            'friday': [],
            'saturday': [],
            'sunday': []
        }
        
        day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for slot in time_slots:
            day_index = slot.start_time.weekday()
            day_name = day_names[day_index]
            weekly_pattern[day_name].append(slot)
        
        return weekly_pattern
    
    async def _calculate_monthly_variations(self, schedule_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate monthly availability variations"""
        # Simplified implementation - in practice would analyze historical data
        monthly_variations = {}
        
        for month in calendar.month_name[1:]:  # Skip empty string at index 0
            # Mock monthly variation (in real implementation, analyze historical patterns)
            if month.lower() in ['december', 'january']:
                monthly_variations[month.lower()] = 0.7  # Lower availability during holidays
            elif month.lower() in ['june', 'july', 'august']:
                monthly_variations[month.lower()] = 0.8  # Summer variations
            else:
                monthly_variations[month.lower()] = 1.0  # Normal availability
        
        return monthly_variations
    
    async def _calculate_seasonal_adjustments(self, schedule_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate seasonal schedule adjustments"""
        return {
            'spring': 1.0,
            'summer': 0.9,  # Slightly lower due to vacations
            'fall': 1.0,
            'winter': 0.8   # Lower due to holidays and weather
        }
    
    async def _find_availability_matches(
        self,
        patterns: List[SchedulePattern]
    ) -> List[AvailabilityMatch]:
        """Find availability matches between creator pairs"""
        matches = []
        
        for i, pattern_a in enumerate(patterns):
            for j, pattern_b in enumerate(patterns[i+1:], i+1):
                match = await self._calculate_pairwise_availability(pattern_a, pattern_b)
                matches.append(match)
        
        return matches
    
    async def _calculate_pairwise_availability(
        self,
        pattern_a: SchedulePattern,
        pattern_b: SchedulePattern
    ) -> AvailabilityMatch:
        """Calculate availability match between two creators"""
        # Find overlapping collaboration windows
        overlapping_slots = []
        
        for slot_a in pattern_a.collaboration_windows:
            for slot_b in pattern_b.collaboration_windows:
                overlap = await self._calculate_time_overlap(slot_a, slot_b)
                if overlap:
                    overlapping_slots.append(overlap)
        
        # Calculate compatibility score
        total_overlap_duration = sum(
            (slot.end_time - slot.start_time).total_seconds() / 3600
            for slot in overlapping_slots
        )
        
        total_available_a = sum(
            (slot.end_time - slot.start_time).total_seconds() / 3600
            for slot in pattern_a.collaboration_windows
        )
        
        total_available_b = sum(
            (slot.end_time - slot.start_time).total_seconds() / 3600
            for slot in pattern_b.collaboration_windows
        )
        
        if total_available_a == 0 or total_available_b == 0:
            compatibility_score = 0.0
        else:
            compatibility_score = total_overlap_duration / min(total_available_a, total_available_b)
        
        # Find optimal meeting times
        optimal_times = await self._find_optimal_meeting_times(overlapping_slots)
        
        # Calculate duration options
        duration_options = await self._calculate_duration_options(overlapping_slots)
        
        # Calculate frequency potential
        frequency_potential = await self._calculate_frequency_potential(overlapping_slots)
        
        # Calculate energy and productivity alignment
        energy_alignment = await self._calculate_energy_alignment(pattern_a, pattern_b)
        productivity_alignment = await self._calculate_productivity_alignment(pattern_a, pattern_b)
        
        return AvailabilityMatch(
            creator_ids=[pattern_a.creator_id, pattern_b.creator_id],
            overlapping_slots=overlapping_slots,
            compatibility_score=compatibility_score,
            optimal_meeting_times=optimal_times,
            collaboration_duration_options=duration_options,
            frequency_potential=frequency_potential,
            energy_alignment=energy_alignment,
            productivity_alignment=productivity_alignment
        )
    
    async def _calculate_time_overlap(self, slot_a: TimeSlot, slot_b: TimeSlot) -> Optional[TimeSlot]:
        """Calculate time overlap between two slots"""
        # Convert to common timezone (UTC)
        start_a = slot_a.start_time.astimezone(timezone.utc)
        end_a = slot_a.end_time.astimezone(timezone.utc)
        start_b = slot_b.start_time.astimezone(timezone.utc)
        end_b = slot_b.end_time.astimezone(timezone.utc)
        
        # Find overlap
        overlap_start = max(start_a, start_b)
        overlap_end = min(end_a, end_b)
        
        if overlap_start < overlap_end:
            # Calculate combined properties
            avg_productivity = (slot_a.productivity_level + slot_b.productivity_level) / 2
            avg_energy = (slot_a.energy_level + slot_b.energy_level) / 2
            min_availability = min(slot_a.availability_for_collaboration, slot_b.availability_for_collaboration)
            avg_focus = (slot_a.focus_quality + slot_b.focus_quality) / 2
            min_interruption_tolerance = min(slot_a.interruption_tolerance, slot_b.interruption_tolerance)
            
            return TimeSlot(
                start_time=overlap_start,
                end_time=overlap_end,
                activity_type=ActivityType.COLLABORATION,
                productivity_level=avg_productivity,
                availability_for_collaboration=min_availability,
                energy_level=avg_energy,
                focus_quality=avg_focus,
                interruption_tolerance=min_interruption_tolerance,
                timezone='UTC'
            )
        
        return None
    
    async def _find_optimal_meeting_times(self, overlapping_slots: List[TimeSlot]) -> List[Dict[str, Any]]:
        """Find optimal meeting times from overlapping slots"""
        if not overlapping_slots:
            return []
        
        # Score slots based on multiple factors
        scored_slots = []
        for slot in overlapping_slots:
            duration_hours = (slot.end_time - slot.start_time).total_seconds() / 3600
            
            # Quality score based on multiple factors
            quality_score = (
                slot.productivity_level * 0.3 +
                slot.energy_level * 0.3 +
                slot.focus_quality * 0.2 +
                slot.availability_for_collaboration * 0.2
            )
            
            # Bonus for longer duration
            duration_bonus = min(duration_hours / 2.0, 1.0)  # Cap at 2 hours
            
            overall_score = quality_score * (1 + duration_bonus * 0.3)
            
            scored_slots.append({
                'slot': slot,
                'score': overall_score,
                'duration_hours': duration_hours
            })
        
        # Sort by score and return top options
        scored_slots.sort(key=lambda x: x['score'], reverse=True)
        
        optimal_times = []
        for scored_slot in scored_slots[:5]:  # Top 5
            slot = scored_slot['slot']
            optimal_times.append({
                'start_time': slot.start_time.isoformat(),
                'end_time': slot.end_time.isoformat(),
                'quality_score': scored_slot['score'],
                'duration_hours': scored_slot['duration_hours'],
                'recommended_for': self._recommend_meeting_type(slot)
            })
        
        return optimal_times
    
    def _recommend_meeting_type(self, slot: TimeSlot) -> List[str]:
        """Recommend meeting types based on slot characteristics"""
        recommendations = []
        
        if slot.focus_quality >= 0.8:
            recommendations.append("strategic_planning")
            recommendations.append("creative_brainstorming")
        
        if slot.energy_level >= 0.8:
            recommendations.append("high_energy_collaboration")
            recommendations.append("video_recording")
        
        if slot.interruption_tolerance >= 0.7:
            recommendations.append("open_discussion")
            recommendations.append("team_meetings")
        else:
            recommendations.append("focused_work_session")
        
        duration = (slot.end_time - slot.start_time).total_seconds() / 3600
        if duration >= 2:
            recommendations.append("workshop")
            recommendations.append("deep_dive_session")
        elif duration >= 1:
            recommendations.append("regular_meeting")
        else:
            recommendations.append("quick_sync")
            recommendations.append("status_update")
        
        return recommendations
    
    async def _calculate_duration_options(self, overlapping_slots: List[TimeSlot]) -> List[int]:
        """Calculate possible collaboration duration options in minutes"""
        if not overlapping_slots:
            return []
        
        durations = []
        for slot in overlapping_slots:
            duration_minutes = int((slot.end_time - slot.start_time).total_seconds() / 60)
            durations.append(duration_minutes)
        
        # Standard meeting durations that fit within available slots
        standard_durations = [15, 30, 45, 60, 90, 120, 180, 240]
        possible_durations = []
        
        max_duration = max(durations) if durations else 0
        for duration in standard_durations:
            if duration <= max_duration:
                possible_durations.append(duration)
        
        return possible_durations
    
    async def _calculate_frequency_potential(self, overlapping_slots: List[TimeSlot]) -> Dict[str, int]:
        """Calculate meeting frequency potential"""
        if not overlapping_slots:
            return {"daily": 0, "weekly": 0, "monthly": 0}
        
        # Count overlapping slots per week (simplified)
        total_overlap_hours = sum(
            (slot.end_time - slot.start_time).total_seconds() / 3600
            for slot in overlapping_slots
        )
        
        # Estimate based on total available overlap
        if total_overlap_hours >= 10:  # 10+ hours per week
            return {"daily": 5, "weekly": 3, "monthly": 12}
        elif total_overlap_hours >= 5:  # 5-10 hours per week
            return {"daily": 2, "weekly": 2, "monthly": 8}
        elif total_overlap_hours >= 2:  # 2-5 hours per week
            return {"daily": 0, "weekly": 1, "monthly": 4}
        else:
            return {"daily": 0, "weekly": 0, "monthly": 2}
    
    async def _calculate_energy_alignment(
        self,
        pattern_a: SchedulePattern,
        pattern_b: SchedulePattern
    ) -> float:
        """Calculate energy level alignment between creators"""
        # Compare energy patterns during collaboration windows
        energy_correlations = []
        
        for slot_a in pattern_a.collaboration_windows:
            for slot_b in pattern_b.collaboration_windows:
                overlap = await self._calculate_time_overlap(slot_a, slot_b)
                if overlap:
                    # Calculate energy difference
                    energy_diff = abs(slot_a.energy_level - slot_b.energy_level)
                    alignment = 1.0 - energy_diff
                    energy_correlations.append(alignment)
        
        return statistics.mean(energy_correlations) if energy_correlations else 0.5
    
    async def _calculate_productivity_alignment(
        self,
        pattern_a: SchedulePattern,
        pattern_b: SchedulePattern
    ) -> float:
        """Calculate productivity alignment between creators"""
        # Compare productivity patterns during overlap times
        productivity_correlations = []
        
        for slot_a in pattern_a.collaboration_windows:
            for slot_b in pattern_b.collaboration_windows:
                overlap = await self._calculate_time_overlap(slot_a, slot_b)
                if overlap:
                    # Calculate productivity alignment
                    prod_diff = abs(slot_a.productivity_level - slot_b.productivity_level)
                    alignment = 1.0 - prod_diff
                    productivity_correlations.append(alignment)
        
        return statistics.mean(productivity_correlations) if productivity_correlations else 0.5
    
    async def _calculate_overall_compatibility(
        self,
        availability_matches: List[AvailabilityMatch]
    ) -> CompatibilityLevel:
        """Calculate overall schedule compatibility level"""
        if not availability_matches:
            return CompatibilityLevel.POOR
        
        avg_compatibility = statistics.mean([match.compatibility_score for match in availability_matches])
        
        if avg_compatibility >= 0.8:
            return CompatibilityLevel.EXCELLENT
        elif avg_compatibility >= 0.6:
            return CompatibilityLevel.GOOD
        elif avg_compatibility >= 0.4:
            return CompatibilityLevel.MODERATE
        elif avg_compatibility >= 0.2:
            return CompatibilityLevel.LIMITED
        else:
            return CompatibilityLevel.POOR
    
    async def _identify_best_collaboration_windows(
        self,
        patterns: List[SchedulePattern],
        matches: List[AvailabilityMatch]
    ) -> List[Dict[str, Any]]:
        """Identify best collaboration windows for the group"""
        # Collect all optimal meeting times from matches
        all_optimal_times = []
        for match in matches:
            all_optimal_times.extend(match.optimal_meeting_times)
        
        # Score and rank windows
        if not all_optimal_times:
            return []
        
        # Group by time windows and calculate aggregate scores
        time_groups = defaultdict(list)
        for time_info in all_optimal_times:
            # Group by hour of day (simplified)
            start_time = datetime.fromisoformat(time_info['start_time'])
            hour_key = start_time.hour
            time_groups[hour_key].append(time_info)
        
        best_windows = []
        for hour, time_infos in time_groups.items():
            avg_score = statistics.mean([info['quality_score'] for info in time_infos])
            avg_duration = statistics.mean([info['duration_hours'] for info in time_infos])
            
            # Count how many creator pairs can meet at this time
            participation_count = len(time_infos)
            
            best_windows.append({
                'hour': hour,
                'average_quality_score': avg_score,
                'average_duration_hours': avg_duration,
                'participation_count': participation_count,
                'overall_score': avg_score * (1 + participation_count * 0.1)
            })
        
        # Sort by overall score
        best_windows.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return best_windows[:3]  # Top 3 windows
    
    async def _recommend_meeting_frequency(
        self,
        matches: List[AvailabilityMatch],
        patterns: List[SchedulePattern]
    ) -> Dict[str, int]:
        """Recommend meeting frequency based on availability"""
        if not matches:
            return {"daily": 0, "weekly": 0, "monthly": 0}
        
        # Aggregate frequency potential from all matches
        total_daily = sum(match.frequency_potential.get("daily", 0) for match in matches)
        total_weekly = sum(match.frequency_potential.get("weekly", 0) for match in matches)
        total_monthly = sum(match.frequency_potential.get("monthly", 0) for match in matches)
        
        # Average across all pairs
        num_pairs = len(matches)
        if num_pairs > 0:
            return {
                "daily": int(total_daily / num_pairs),
                "weekly": int(total_weekly / num_pairs),
                "monthly": int(total_monthly / num_pairs)
            }
        
        return {"daily": 0, "weekly": 0, "monthly": 0}
    
    async def _optimize_temporal_workflow(
        self,
        patterns: List[SchedulePattern]
    ) -> Dict[str, Any]:
        """Optimize temporal workflow based on creator patterns"""
        # Analyze when each creator is most productive
        creator_peak_times = {}
        for pattern in patterns:
            creator_peak_times[pattern.creator_id] = pattern.peak_productivity_times
        
        # Find complementary work periods
        workflow_optimization = {
            "sequential_work_periods": [],
            "parallel_work_periods": [],
            "handoff_times": [],
            "review_cycles": []
        }
        
        # Sequential periods (when one finishes, another starts)
        all_times = []
        for creator_id, peak_times in creator_peak_times.items():
            for start, end in peak_times:
                all_times.append({
                    'creator': creator_id,
                    'start': start,
                    'end': end,
                    'type': 'peak'
                })
        
        # Sort by time
        all_times.sort(key=lambda x: x['start'])
        
        # Find sequential opportunities
        for i, current in enumerate(all_times):
            for next_period in all_times[i+1:]:
                if (next_period['start'] >= current['end'] and 
                    next_period['start'] <= current['end'] + 2 and  # Within 2 hours
                    next_period['creator'] != current['creator']):
                    
                    workflow_optimization["sequential_work_periods"].append({
                        'first_creator': current['creator'],
                        'first_period': (current['start'], current['end']),
                        'second_creator': next_period['creator'],
                        'second_period': (next_period['start'], next_period['end']),
                        'handoff_time': current['end']
                    })
                    break
        
        # Find parallel opportunities (overlapping peak times)
        for i, current in enumerate(all_times):
            for other in all_times[i+1:]:
                if (other['creator'] != current['creator'] and
                    current['start'] < other['end'] and other['start'] < current['end']):
                    
                    overlap_start = max(current['start'], other['start'])
                    overlap_end = min(current['end'], other['end'])
                    
                    if overlap_end > overlap_start:
                        workflow_optimization["parallel_work_periods"].append({
                            'creators': [current['creator'], other['creator']],
                            'overlap_period': (overlap_start, overlap_end),
                            'duration_hours': overlap_end - overlap_start
                        })
        
        return workflow_optimization
    
    async def _analyze_schedule_conflicts(
        self,
        patterns: List[SchedulePattern]
    ) -> Dict[str, Any]:
        """Analyze potential schedule conflicts"""
        conflicts = {
            "timezone_conflicts": [],
            "pattern_mismatches": [],
            "availability_gaps": [],
            "energy_misalignments": []
        }
        
        # Timezone conflicts
        timezones = [pattern.timezone for pattern in patterns]
        unique_timezones = set(timezones)
        
        if len(unique_timezones) > 1:
            for tz1 in unique_timezones:
                for tz2 in unique_timezones:
                    if tz1 != tz2:
                        try:
                            tz1_obj = pytz.timezone(tz1)
                            tz2_obj = pytz.timezone(tz2)
                            now = datetime.now(pytz.UTC)
                            diff = abs((now.astimezone(tz1_obj).utcoffset() - 
                                      now.astimezone(tz2_obj).utcoffset()).total_seconds() / 3600)
                            
                            if diff > 6:  # Significant timezone difference
                                conflicts["timezone_conflicts"].append({
                                    'timezone1': tz1,
                                    'timezone2': tz2,
                                    'difference_hours': diff,
                                    'severity': 'high' if diff > 10 else 'medium'
                                })
                        except:
                            pass
        
        # Pattern mismatches
        primary_patterns = [pattern.primary_pattern for pattern in patterns]
        pattern_variety = len(set(primary_patterns))
        
        if pattern_variety > 2:
            conflicts["pattern_mismatches"].append({
                'issue': 'High variety in schedule patterns',
                'patterns': list(set(primary_patterns)),
                'impact': 'Coordination difficulty'
            })
        
        return conflicts
    
    async def _optimize_productivity_alignment(
        self,
        patterns: List[SchedulePattern]
    ) -> Dict[str, Any]:
        """Optimize productivity alignment across creators"""
        optimization = {
            "synchronized_high_productivity_periods": [],
            "staggered_work_recommendations": [],
            "energy_level_optimization": [],
            "focus_time_protection": []
        }
        
        # Find synchronized high productivity periods
        all_peak_times = []
        for pattern in patterns:
            for start, end in pattern.peak_productivity_times:
                all_peak_times.append({
                    'creator': pattern.creator_id,
                    'start': start,
                    'end': end
                })
        
        # Group overlapping peak times
        overlapping_groups = []
        for i, peak1 in enumerate(all_peak_times):
            group = [peak1]
            for j, peak2 in enumerate(all_peak_times[i+1:], i+1):
                if (peak1['start'] < peak2['end'] and peak2['start'] < peak1['end'] and
                    peak1['creator'] != peak2['creator']):
                    group.append(peak2)
            
            if len(group) > 1:
                overlap_start = max(p['start'] for p in group)
                overlap_end = min(p['end'] for p in group)
                
                if overlap_end > overlap_start:
                    optimization["synchronized_high_productivity_periods"].append({
                        'creators': [p['creator'] for p in group],
                        'time_period': (overlap_start, overlap_end),
                        'duration_hours': overlap_end - overlap_start
                    })
        
        return optimization
    
    async def _assess_long_term_sustainability(
        self,
        patterns: List[SchedulePattern]
    ) -> Dict[str, Any]:
        """Assess long-term sustainability of collaboration schedule"""
        sustainability = {
            "workload_balance": {},
            "burnout_risk_factors": [],
            "seasonal_adjustments_needed": [],
            "flexibility_requirements": [],
            "sustainability_score": 0.0
        }
        
        # Assess workload balance
        total_collaboration_hours = {}
        for pattern in patterns:
            total_hours = sum(
                (slot.end_time - slot.start_time).total_seconds() / 3600
                for slot in pattern.collaboration_windows
            )
            total_collaboration_hours[pattern.creator_id] = total_hours
        
        if total_collaboration_hours:
            avg_hours = statistics.mean(total_collaboration_hours.values())
            max_hours = max(total_collaboration_hours.values())
            min_hours = min(total_collaboration_hours.values())
            
            sustainability["workload_balance"] = {
                "average_weekly_hours": avg_hours,
                "max_weekly_hours": max_hours,
                "min_weekly_hours": min_hours,
                "balance_ratio": min_hours / max_hours if max_hours > 0 else 0
            }
            
            # Burnout risk factors
            if max_hours > 40:
                sustainability["burnout_risk_factors"].append("Excessive collaboration hours")
            
            if max_hours / min_hours > 2:
                sustainability["burnout_risk_factors"].append("Uneven workload distribution")
        
        # Seasonal adjustments
        seasonal_impacts = []
        for pattern in patterns:
            for season, adjustment in pattern.seasonal_adjustments.items():
                if adjustment < 0.8:
                    seasonal_impacts.append(f"{pattern.creator_id} has reduced availability in {season}")
        
        sustainability["seasonal_adjustments_needed"] = seasonal_impacts
        
        # Calculate overall sustainability score
        balance_score = sustainability["workload_balance"].get("balance_ratio", 0)
        risk_penalty = len(sustainability["burnout_risk_factors"]) * 0.1
        seasonal_penalty = len(sustainability["seasonal_adjustments_needed"]) * 0.05
        
        sustainability["sustainability_score"] = max(0, balance_score - risk_penalty - seasonal_penalty)
        
        return sustainability


# Export main classes
__all__ = [
    'TemporalAnalyzer',
    'SchedulePattern',
    'TimeSlot',
    'TemporalPatterns',
    'TimeAnalysis',
    'ScheduleCompatibility',
    'AvailabilityMatch',
    'SchedulePattern',
    'ActivityType',
    'CompatibilityLevel'
]